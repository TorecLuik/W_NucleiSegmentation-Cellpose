import sys
import os
import shutil
import subprocess
import imageio
import numpy as np
from cytomine.models import Job
from biaflows import CLASS_OBJSEG, CLASS_SPTCNT, CLASS_PIXCLA, CLASS_TRETRC, CLASS_LOOTRC, CLASS_OBJDET, CLASS_PRTTRK, CLASS_OBJTRK
from biaflows.helpers import BiaflowsJob, prepare_data, upload_data, upload_metrics, get_discipline


def main(argv):
    base_path = "{}".format(os.getenv("HOME")) # Mandatory for Singularity
    with BiaflowsJob.from_cli(argv) as bj:
        # Change following to the actual problem class of the workflow
        problem_cls = get_discipline(bj, default=CLASS_OBJSEG)
        
        bj.job.update(status=Job.RUNNING, progress=0, statusComment="Initialisation...")
        
        # 1. Prepare data for workflow
        in_imgs, gt_imgs, in_path, gt_path, out_path, tmp_path = prepare_data(problem_cls, bj, is_2d=True, **bj.flags)

        # Make sure all images have at least 224x224 dimensions
        # and that minshape / maxshape * minshape >= 224
        resized = {}
        for bfimg in in_imgs:
            fn = os.path.join(in_path, bfimg.filename)
            img = imageio.imread(fn)
            minshape = min(img.shape[:2])
            maxshape = max(img.shape[:2])
            if minshape != maxshape or minshape < 224:
                resized[bfimg.filename] = img.shape
                padshape = []
                for i in range(2):
                    if img.shape[i] < max(224,maxshape):
                        padshape.append((0,max(224,maxshape)-img.shape[i]))
                    else:
                        padshape.append((0,0))
                if len(img.shape) == 3:
                    padshape.append((0,0))
                img = np.pad(img, padshape, 'constant', constant_values=0)
            imageio.imwrite(os.path.join(tmp_path, bfimg.filename), img)

        # 2. Run image analysis workflow
        bj.job.update(progress=25, statusComment="Launching workflow...")

        # Add here the code for running the analysis script
        cmd = ["python", "-m", "cellpose", "--dir", tmp_path, "--pretrained_model", "nuclei", "--save_tif", "--no_npy", "--all_channels", "--diameter", "{:f}".format(bj.parameters.diameter), "--cellprob_threshold", "{:f}".format(bj.parameters.prob_threshold)]
        status = subprocess.run(cmd)

        if status.returncode != 0:
            print("Running Cellpose failed, terminate")
            sys.exit(1)

        # Crop to original shape
        for bimg in in_imgs:
            shape = resized.get(bimg.filename, None)
            if shape:
                img = imageio.imread(os.path.join(tmp_path,bimg.filename_no_extension+"_cp_masks.tif"))
                img = img[0:shape[0], 0:shape[1]]
                imageio.imwrite(os.path.join(out_path,bimg.filename), img)
            else:
                shutil.copy(os.path.join(tmp_path,bimg.filename_no_extension+"_cp_masks.tif"), os.path.join(out_path,bimg.filename))
        
        # 3. Upload data to BIAFLOWS
        upload_data(problem_cls, bj, in_imgs, out_path, **bj.flags, monitor_params={
            "start": 60, "end": 90, "period": 0.1,
            "prefix": "Extracting and uploading polygons from masks"})
        
        # 4. Compute and upload metrics
        bj.job.update(progress=90, statusComment="Computing and uploading metrics...")
        upload_metrics(problem_cls, bj, in_imgs, gt_path, out_path, tmp_path, **bj.flags)

        # 5. Pipeline finished
        bj.job.update(progress=100, status=Job.TERMINATED, status_comment="Finished.")


if __name__ == "__main__":
    main(sys.argv[1:])
