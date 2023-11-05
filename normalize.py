#!/usr/bin/env python3

# Written by Gem Newman. This work is licenced under the MIT License.

# Note that ffmpeg doesn't do a perfect job of determining peak amplitude, so
# here we attempt to normalize to around -0.5 dB to avoid going above 0.0 dB.


from argparse import ArgumentParser
from glob import glob
import re
import subprocess
import os


def main():
    parser = ArgumentParser(
        description='Performs peak normalization on the specified audio file.')
    parser.add_argument('file', help='The audio file to normalize.')
    parser.add_argument("--verbose", '-v', action='store_true')
    args = parser.parse_args()

    f = args.file

    # Detect (approximate) peak amplitude
    # This will fail if there are quotation marks in the file name
    result = subprocess.run(
        f'ffmpeg -i "{f}" -af volumedetect -vn -sn -dn -f null /dev/null 2>&1 '
        '| grep "max_volume:"', shell=True, capture_output=True
    )
    if result.returncode:
        print(str(result.stderr))
        exit()

    target = re.search(r'max_volume: (-?\d+\.\d+)', str(result.stdout))

    if not target:
        print('Unable to determine peak amplitude.')
        exit()

    amp = float(target.group(1))

    if args.verbose:
        print(f'Current peak amplitude: {amp} dB')

    if amp < -0.5:
        amp = -amp - 0.5

        if args.verbose:
            print(f'Amplifying {f} by {amp} dB...')

        # Normalize the file
        # This will fail if there are quotation marks in the file name
        result = subprocess.run(
            f'ffmpeg -i "{f}" -write_xing 0 -af "volume={amp} dB" '
            f'-c:a libmp3lame "new.{f}"',
            shell=True, capture_output=True
        )
        if result.returncode:
            print(str(result.stderr))
            exit()

        os.replace(f'new.{f}', f)


if __name__ == "__main__":
    main()

