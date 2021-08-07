import os
import subprocess


def poc_subprocess():
    path = 'Notepad++.exe'
    subprocess.Popen(args=f'{path}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return_code = os.system(f'TASKKILL /IM {path} /F')
    if return_code != 0:
        raise AssertionError(f'{path} delete failed: {return_code}!')


if __name__ == "__main__":
    pass
