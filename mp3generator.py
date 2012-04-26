#!/usr/bin/python

import aifc
import random
import os
from optparse import OptionParser
from subprocess import call

def which(program):
    """Check if program exists"""
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def generate_aiff(output, nchannels=1, sampwidth=2, framerate=44100, nframes=8):
    """Generates a random AIFF file"""
    aiff = aifc.open(output, 'w')
    aiff.setparams([nchannels, sampwidth, framerate, nframes, 'NONE',
    'Uncompressed file'])
    
    data = ''
    for i in range(nchannels * sampwidth * nframes):
        data += chr(random.randint(0, 255))
    
    aiff.writeframes(data)
    aiff.close()


def aiff_to_mp3(aiff, mp3, bitrate=192*1024, framerate=44100):
    """Converts an AIFF file to MP3 using ffmpeg"""
    call(['ffmpeg', '-i', aiff, '-f', 'mp3', '-ab', str(bitrate), '-ar',
        str(framerate), mp3])


def generate(output, nchannels=1, sampwidth=2, framerate=44100, nframes=8,
        bitrate=192*1024):
    """Generates a random MP3 file"""
    # Assert ffmpeg is available
    if not which('ffmpeg'):
        print "Error: ffmpeg not available"
        return 1

    # Assert MP3 extension to output file
    if not output.endswith('.mp3'):
        output += '.mp3'

    # Create an AIFF version
    aiff_output = output.replace('.mp3', '.aiff')
    
    generate_aiff(aiff_output, nchannels, sampwidth, framerate, nframes)
    aiff_to_mp3(aiff_output, output, bitrate, framerate)


if __name__ == "__main__":
    parser = OptionParser(usage='Usage: %prog [options] <output.mp3>',
            version='%prog 1.0', description='Random MP3 file generator')
    parser.add_option('-c', '--channels', action='store', default='mono',
            choices=['mono', 'stereo'], help='Number of channels',
            metavar='<channels>')
    parser.add_option('-w', '--sampwidth', action='store', type='int',
            default=2, help='Number of bytes of each sample',
            metavar='<sampwidth>')
    parser.add_option('-r', '--framerate', action='store', type='int',
            default=44100, help='Sampling frequency in frames per second',
            metavar='<framerate>')
    parser.add_option('-n', '--nframes', action='store', type='int', default=8,
            help='Number of frames', metavar='<nframes>')
    parser.add_option('-b', '--bitrate', action='store', type='int',
            default=128, help='Bit rate used in mp3 encoding (in kb/s)',
            metavar='<bitrate>')
    (opts, args) = parser.parse_args()

    if len(args) != 1:
        parser.error('Wrong number of arguments')

    output = args[0]

    if opts.channels == 'mono':
        nchannels = 1
    else:
        nchannels = 2

    generate(output, nchannels, opts.sampwidth, opts.framerate, opts.nframes,
            opts.bitrate*1000)

