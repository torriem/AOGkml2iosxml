#!/usr/bin/python3

import isoxml
import bs4

class KML2ISOXMLException(Exception):
    pass

class KML2ISOXML(isoxml.ISOXML):
    def add_kml(self, field_name, kml_bytes):
        parser=bs4.BeautifulSoup(kml_bytes,'lxml-xml')
        folders = parser.find_all('Folder')
        
        if not len(folders):
            raise KML2ISOXMLException("KML does not have AOG folders and placemarks in it.")

        for f in folders:
            folder_name = f.find('name').contents[0]
            
            if folder_name == 'AB_Lines':
                placemarks = f.find_all('Placemark')
                for p in placemarks:
                    ab_name = p.find('name').contents[0]
                    ab_points = p.find('coordinates').contents[0].strip().split(' ')
                    # convert list of string coordinates to tuples of lat and lon
                    # numbers
                    ab_points = [ tuple( float(x) for x in c.split(',')[:2]) for c in ab_points]
                    self.make_ab_line(field_name, ab_name, ab_points[0], ab_points[1])
            elif folder_name == 'Boundaries':
                placemarks = f.find_all('Placemark')
                for p in placemarks:
                    boundary_name = p.find('name').contents[0]

                    # should only be one polygon, for now we only use the outer
                    # boundary of that polygon.
                    bnd_points = p.Polygon.outerBoundaryIs.LinearRing.coordinates.contents[0]
                    bnd_points = bnd_points.strip().split(' ')
                    bnd_points = [ tuple( float(x) for x in c.split(',')[:2]) for c in bnd_points]

                    self.make_boundary(field_name, boundary_name, bnd_points)
        else:
            pass


            # ignore the rest of the folders

if __name__ == '__main__':
    import argparse
    import os

    argparser = argparse.ArgumentParser(prog='kml2isoxml.py', 
                                        description='This script converts a single AgOpenGPS Field.kml file to ISOXML format, converting only the AB Lines and Boundaries') 
    argparser.add_argument('-d', '--outputdir', type=str, help='output directory to create isoxml files in, defaults to "TASKDATA"')
    argparser.add_argument('-f', '--farm', type=str, help='Farm name')
    argparser.add_argument('-o', '--operator', type=str, help='Operator name')
    argparser.add_argument('field_name', help = 'Name of the field that the kml belongs to')
    argparser.add_argument('kml_file', help = 'AOG-produced Field.kml containing boundaries and AB Lines')

    args = argparser.parse_args()

    if not args.outputdir:
        args.outputdir="TASKDATA"
    if not args.farm:
        args.farm = 'AgOpenGPSFarm'
    if not args.operator:
        args.operator = 'AgOpenGPS'

    os.makedirs(args.outputdir,exist_ok=True)

    k = KML2ISOXML(args.operator, args.farm)
    kml = open(args.kml_file, 'r').read()
    k.add_kml(args.field_name, kml)
    k.write(args.outputdir)
