## For the swift tests you will need three objects to upload for the test
## examples below are a 512K object, a 500M object, and 1G object
dd if=/dev/zero of=single_small bs=512 count=1024
dd if=/dev/zero of=single_medium bs=512 count=1024000
dd if=/dev/zero of=single_large bs=1024 count=1024000
