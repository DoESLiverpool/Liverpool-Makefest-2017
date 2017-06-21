#!/usr/bin/env python3

import csv, re, os, shutil, argparse, urllib
#import lxml.etree.ElementTree as ET
from lxml import etree

SVG_FOLDER = 'svgs'
PDF_FOLDER = 'pdfs'

def main():
    # parse some flags here
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infile", help="ods or xlsx input file", default='makers.ods')
    parser.add_argument("-t", "--template", help="SVG template filename", default='template.svg')
    parser.add_argument("-o", "--outfile", help="PDF outfile name", default='makers.pdf')
    parser.add_argument("-c", "--keepcsv", help="Keep the temporary CSV file", default=False, action='store_true')
    parser.add_argument("-s", "--keepsvgs", help="Keep temporary SVG files", default=False, action='store_true')
    parser.add_argument("-p", "--keeppdfs", help="Keep temporary PDF files", default=False, action='store_true')
    parser.add_argument("-x", "--debugflag", help="process one entry and stop", default=False, action='store_true')
    args = parser.parse_args()

    infile = args.infile
    template = args.template
    outfile = args.outfile
    keep_pdfs = args.keeppdfs
    keep_svgs = args.keepsvgs
    keep_csv = args.keepcsv
    debugflag = args.debugflag

    # generate the csv file (comma separated, double quotetd, utf-8)
    # TODO: check if libreoffice is running, otherwise this generation fails silently
    # because the lockfile exists
    os.system('libreoffice --headless --convert-to csv:"Text - txt - csv (StarCalc)":44,34,76,1,1 --outdir . ' + infile)
    csvfilename = re.sub(r'\.[a-zA-Z0-9]+$', '', infile) + '.csv'

    # check the required dirs exist
    if not os.path.exists(SVG_FOLDER):
        os.makedirs(SVG_FOLDER)
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)

    # create each file from line of csv file
    with open(csvfilename) as csvfile:
        reader = csv.DictReader(csvfile)
        i = 1
        for row in reader:
            # generate the required variables to substitute into the SVG
            filesafe_name = re.sub(r"[^\w\s]", '', row['{title}'])
            filesafe_name = re.sub(r"\s+", '-', filesafe_name)
            filesafe_name = str(i).zfill(2) + '-' + filesafe_name.strip()
            filesafe_name = (filesafe_name[:14]) if len(filesafe_name) > 14 else filesafe_name
            title = row['{title}'].strip()
            name = row['{name}'].strip()
            description = row['{description}'].replace('_x000D_','')
            # standardise *some* of the possible twitter and web inputs
            twitter = '@' + row['{twitter}'].strip().replace('http://','').replace('https://','').replace('twitter.com/','').lstrip('@').strip()
            website = row['{website}'].strip().replace('http://','').replace('https://','').replace('www.','').strip()

            # parse vars to standardise text input


            # replace the placeholders in the new file
            svg_file = SVG_FOLDER + '/' + filesafe_name + '.svg'
            # read the svg template file in
            #tree = ET.parse(template)
            #root = tree.getroot()
            tree = etree.parse(template)
            root = tree.getroot()
            for para in root.findall('.//{http://www.w3.org/2000/svg}flowPara'):
                if para.text == '{title}':
                    para.text = title
                    if len(title) >= 34:
                        # reduce the text size
                        parent = para.find('..')
                        style_tag = parent.attrib['style']
                        # find the current font size
                        font_size_tag = re.search('font-size:[0-9.]+px;', style_tag).group()
                        font_size = float(re.search(r'[0-9.]+', font_size_tag).group())
                        if len(title) >= 50:
                            font_size = font_size*0.75
                        else:
                            font_size = font_size*0.85
                        style_tag = re.sub(r'font-size:[0-9.]+px;', 'font-size:' + str(font_size) + 'px;', style_tag)
                        parent.attrib['style'] = style_tag
                        print('title font-size: ' + str(font_size) + ' px;')
                        #print(parent.attrib['style'])
                elif para.text == '{name}':
                    para.text = name
                elif para.text == '{description}':
                    para.text = description
                    if len(description) >= 512:
                        # reduce the text size
                        parent = para.find('..')
                        style_tag = parent.attrib['style']
                        # find the current font size
                        font_size_tag = re.search('font-size:[0-9.]+px;', style_tag).group()
                        font_size = float(re.search(r'[0-9.]+', font_size_tag).group())
                        if len(description) > 1200:
                            font_size = font_size*0.65
                        elif len(description) > 800:
                            font_size = font_size*0.75
                        else:
                            font_size = font_size*0.85
                        style_tag = re.sub(r'font-size:[0-9.]+px', 'font-size:' + str(font_size) + 'px', style_tag)
                        parent.attrib['style'] = style_tag
                        print('description font-size: ' + str(font_size) + ' px;')
                elif para.text == '{twitter}':
                    if twitter != '@': # is empty
                        para.text = twitter
                    else:
                        para.text = ''
                elif para.text == '{website}':
                    if website[-1:] == '/':
                        para.text = website[:-1]
                    else:
                        para.text = website
            # write the adjusted svg
            tree.write(svg_file)

            pdf_file = PDF_FOLDER + '/' + filesafe_name + '.pdf'
            os.system('inkscape --without-gui --file ' + svg_file + ' --export-text-to-path --export-area-page --export-pdf ' + pdf_file)

            print('Created: ' + title)
            i+=1

            if debugflag == True:
                print ('Filename: ' + filesafe_name)
                print ('Name: ' + name)
                print ('Title: ' + title + ' [' + str(len(title)) + ']')
                print ('Description: ' + description + ' [' + str(len(description)) + ']')
                print ('Twitter: ' + twitter)
                print ('Website: ' + website)
                quit()

    # concatenate all the pdf pages
    os.chdir(PDF_FOLDER)
    os.system('pdftk *.pdf output ../' + outfile)
    os.chdir('..')

    # cleanup temporary files
    if keep_csv == False:
        os.remove(csvfilename)
    if keep_svgs == False:
        shutil.rmtree(SVG_FOLDER)
    if keep_pdfs == False:
        shutil.rmtree(PDF_FOLDER)

if __name__ == "__main__":
    main()
