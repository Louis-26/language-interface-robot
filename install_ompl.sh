# Set variables
URL="https://github.com/ompl/ompl/releases/download/1.7.0/wheels-ubuntu-latest-x86_64.zip"
ZIPFILE="wheels-ubuntu-latest-x86_64.zip"
DESTDIR="ompl_wheels"
# Download the zip file
wget -O $ZIPFILE $URL

# Create directory to unzip into
mkdir -p $DESTDIR

# Unzip downloaded file into the directory
unzip -o $ZIPFILE -d $DESTDIR

# List contents to confirm
ls -l $DESTDIR

# (Optional) Install the Python wheel for Python 3.10
# Adjust the filename if needed based on what's inside $DESTDIR
pip install $DESTDIR/ompl-1.7.0-cp310-cp310-manylinux_2_28_x86_64.whl

rm -rf $DESTDIR $ZIPFILE