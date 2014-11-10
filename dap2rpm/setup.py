import subprocess

def setup_rpmdevtree():
    rst = subprocess.Popen(['rpmdev-setuptree'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = rst.communicate()
    if rst.returncode != 0:
        raise  # TODO: message

def has_rpmdev_packager():
    has_rpk = subprocess.Popen(['which', 'rpmdev-packager'], stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    out = has_rpk.communicate()
    if has_rpk.returncode != 0:
        raise  # TODO: message

def setup():
    try:
        setup_rpmdevtree()
    except Exception as e:
        raise  # TODO

    try:
        has_rpmdev_packager()
    except Exception as e:
        raise  # TODO
