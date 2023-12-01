import os
#import datetime

#today = datetime.datetime.now().strftime('%y%m%d')

class ISOXML(object):
    
    def __init__(self, operator, farm):
        self.operator = operator
        self.farm = farm
        self.fields = {}
        self.counters = { 'ggp': 0,
                          'gpn': 0,
                        }


    def make_ab_line(self, field_name, abline_name, a, b):
        if not field_name in self.fields:
            self.fields[field_name] = []

        #abline_name = "%s_%s" % (abline_name, today)
        #print ("field %s, isoxml abline_name is %s" % (field_name, abline_name))

        field = self.fields[field_name]
        field.append('\t\t <GGP A="GGP-%d" B="%s" >\r\n' % (self.counters['ggp'], abline_name))
        field.append('\t\t\t <GPN A="GPN-%d" B="%s" C="1" E="1" F="1" >\r\n' % (self.counters['gpn'], abline_name))
        field.append('\t\t\t\t <LSG A="5" >\r\n')
        field.append('\t\t\t\t\t <PNT A="6" C="%.9f" D="%.9f" />\r\n' % (a[1], a[0]))
        field.append('\t\t\t\t\t <PNT A="7" C="%.9f" D="%.9f" />\r\n' % (b[1], b[0]))
        field.append('\t\t\t\t </LSG>\r\n')
        field.append('\t\t\t </GPN>\r\n')
        field.append('\t\t </GGP>\r\n')
        self.counters['ggp'] +=1
        self.counters['gpn'] +=1

    def make_boundary(self, field_name, boundary_name, boundary_points):
        if not field_name in self.fields:
            self.fields[field_name] = []

        field = self.fields[field_name]

        #boundary_name = "%s_%s" % (boundary_name, today)

        field.append('\t\t <PLN A="1" B="%s" P094_Subtype="0" P094_Impassable="0" >\r\n' % boundary_name)
        field.append('\t\t\t <LSG A="1" >\r\n')
        
        for bp in boundary_points:
            field.append('\t\t\t\t <PNT A="2" C="%.9f" D="%.9f" />\r\n' % (bp[1], bp[0]))

        field.append('\t\t\t </LSG>\r\n')
        field.append('\t\t </PLN>\r\n')

    def write(self, dirname, which_field=None):
        if not os.path.exists(dirname):
            os.mkdir(dirname)

        taskdata = open (os.path.join(dirname,"TASKDATA.XML"), "w")
        with taskdata:
            taskdata.write('<?xml version="1.0" encoding="UTF-8"?>\r\n')
            taskdata.write('<ISO11783_TaskData VersionMajor="4" VersionMinor="2" ManagementSoftwareManufacturer="" ManagementSoftwareVersion="0" TaskControllerManufacturer="CNH" TaskControllerVersion="31.21.0.0" DataTransferOrigin="2" >\r\n')
            taskdata.write('\t <XFR A="CTR00000" B="1"/>\r\n')
            taskdata.write('\t <XFR A="FRM00000" B="1"/>\r\n')
            taskdata.write('\t <XFR A="PFD00000" B="1"/>\r\n')
            taskdata.write('</ISO11783_TaskData>\r\n')

        ctr = open (os.path.join(dirname, "CTR00000.XML"), "w")
        with ctr:
            ctr.write('<?xml version="1.0" encoding="UTF-8"?>\r\n')
            ctr.write('<XFC >\r\n')
            ctr.write('\t <CTR A="CTR-0" B="%s" />\r\n' % self.operator)
            ctr.write('</XFC>\r\n')

        frm = open (os.path.join(dirname, "FRM00000.XML"), "w")
        with frm:
            frm.write('<?xml version="1.0" encoding="UTF-8"?>\r\n')
            frm.write('<XFC >\r\n')
            frm.write('\t <FRM A="FRM-0" B="%s" I="CTR-0" />\r\n' % self.farm)
            frm.write('</XFC>\r\n')

        pfd_id = 0
        pfd = open (os.path.join(dirname, "PFD00000.XML"), "w")
        with pfd:
            pfd.write('<?xml version="1.0" encoding="UTF-8"?>\r\n')
            pfd.write('<XFC >\r\n')
            for field in self.fields:
                if which_field is not None and not field in which_field:
                    # only output one field
                    continue
                print ("ISOXML Processing field %s" % field)
                pfd.write('\t <PFD A="PFD-%d" C="%s" D="0" E="CTR-0" F="FRM-0" >\r\n' % (pfd_id, field))
                for line in self.fields[field]:
                    pfd.write(line)
                pfd.write('\t </PFD>\r\n')
            pfd.write('</XFC>\r\n')




