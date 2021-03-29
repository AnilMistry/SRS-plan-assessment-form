# This is a sample Python script.
"""
        SRS Plan Assessment form v6

        TODO:
         - create UI for user can edit PTV's used in calc
         - format the PDF to look like the spreadsheet
         - check calculations for indicies
         - Automatically open PDF upon finishing
         - create unique filename for output PDF
         - Add planner name and data
         - Add GTV and PTV volumes next to pat info << NOT TRIVIAL
         -

"""

import json
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, PageBreak, Paragraph
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet


class PTV:
    """Data and calculations for each PTV.
    TODO: add bool:"Selected" for initial UI, only calc true
    """

    def __init__(self, target):
        """Read in ptv object from PTVS in json file and
        create data"""
        self.ptvName = target['ptv_name']
        self.ptvVol = float(target['ptv_vol'])
        self.gtvVol = float(target['gtv_vol'])
        self.ptvV100 = float(target['ptv_v100'])
        self.ptvDose = float(target['ptv_dose'])
        self.ptvD100 = float(target['ptv_d100'])
        self.ptvD99 = float(target['ptv_d99'])
        self.bodyV100 = float(target['body_v100'])
        self.bodyV80 = float(target['body_v80'])
        self.bodyV50 = float(target['body_v50'])
        self.bodyV30 = float(target['body_v30'])
        self.bodyV10 = float(target['body_v10'])
        self.brainPTV_V10 = float(target['brain_ptv_v10'])
        self.brainPTV_V12 = float(target['brain_ptv_v12'])

    def conformity_index(self):
        return self.bodyV100/self.ptvVol

    def target_conf_index(self):
        return self.ptvV100/self.ptvVol

    def selectivity_index(self):
        return self.ptvV100/self.bodyV100

    def paddick_index(self):
        return (self.ptvV100 * self.ptvV100)/(self.ptvVol * self.bodyV100)

    def gradient_index_80(self):
        return self.bodyV80/self.bodyV100

    def gradient_index_50(self):
        return self.bodyV50/self.bodyV100

    def gradient_index_30(self):
        return self.bodyV30/self.bodyV100

    def v50_ptv_vol(self):
        return self.bodyV50/self.ptvVol


def createTables(data):
    """ Generate the indicies table and
     target table, PTV by PTV, row by row.
     Then transpose the tables so PTV's are columns
     TODO: create individual ParagraphStyles for
            -column headers
            -text columns
            -float values
        to replace stylen, for better formatting control
        Put all text into paragraph objects

     """
    styles = getSampleStyleSheet()
    stylen = styles["BodyText"]


    indicies_data = [["Index", Paragraph("Conformity Index (RTOG)", stylen),
                      Paragraph("Target Coverage Ratio", stylen),
                      "Selectivity Index", "Paddick index", "80% Gradient Index",
                      "50% Gradient Index", "30% Gradient Index", "V50%/PTV vol",
                      "V12"],
                ["Formula",
                 Paragraph("Body V100%(cc)/PTV Vol (cc)", stylen),
                 Paragraph("PTV V100%(cc) /PTV Vol (cc)", stylen),
                 Paragraph("PTV V100%(cc) /Body V100%(cc)", stylen),
                 Paragraph("Target Coverage*Selectivity", stylen),
                 Paragraph("Body V80%(cc) /Body V100%(cc)", stylen),
                 Paragraph("Body V50%(cc) /Body V100%(cc)", stylen),
                 Paragraph("Body V30%(cc) /Body V100%(cc)", stylen),
                 Paragraph("BodyV50%(cc) /PTV vol (cc)", stylen),
                 Paragraph("Brain-PTV V12Gy)", stylen)],
                ["Description",
                 Paragraph("Volume 100% isodose compared to PTV vol.", stylen),
                 Paragraph("How well PTV is covered by 100% isodose", stylen),
                 Paragraph("Spillage of 100% isodose outside PTV", stylen),
                 Paragraph("Combination of coverage and selectivity", stylen),
                 Paragraph("Tightness of 80% to 100%", stylen),
                 Paragraph("Tightness of 50% to 100%", stylen),
                 Paragraph("Tightness of 30% to 100%", stylen),
                 Paragraph("Spillage combined with GI 50%*", stylen),
                 Paragraph("Normal Brain toxicity", stylen)]]

    target_data = [["Structure", "GTV", "PTV", "PTV", "PTV", "PTV", "PTV",
                    "Body (PTV_eval)", "Body (PTV_eval)", "Body (PTV_eval)",
                    "Body (PTV_eval)", "Body (PTV_eval)", "Brain-PTV", "Brain-PTV"],
                ["Parameter", "Volume (cc)", "Volume (cc)", "V100%(cc)", "Dose (Gy)",
                 "D100% (Gy)", "D99%(Gy)", "V100%(cc)", "V80%(cc)", "V50%(cc)",
                 "V30%(cc)", "V10%(cc)", "V10Gy(cc)", "V12Gy(cc)"],
                ["Description", "Volume of structure", "Volume of structure",
                 "Treated Target Volume (TTV)", "Prescription Dose", "Minimum Dose",
                 "Near Minimum Dose", "Volume of 100% isodose (Presc. Isodose Vol)",
                 "Volume of 80% isodose", "Volume of 50% isodose", "Volume of 30% isodose",
                 "Volume of 10% isodose", "Volume of 10Gy isodose in Brain",
                 "Volume of 12Gy isodose in Brain"]]

    # iterate through ptvs, create PTV class instances, and create table rows.
    # Possibly need to delete PTV instances after they are used?
    for item in data['ptvs']:
        i = PTV(item)
        target_data.append(targetDataLine(i))
        indicies_data.append(indDataLine(i))

    # transpose tables so PTVS are columns
    target_data = [*zip(*target_data)]
    indicies_data = [*zip(*indicies_data)]

    return [indicies_data, target_data]


def targetDataLine(x):
    """ Read in PTV object, return the target data in correct format"""
    return [x.ptvName, "%.2f" % x.ptvVol,"%.2f" % x.gtvVol,
            "%.2f" % x.ptvV100,"%.2f" % x.ptvDose, "%.2f" % x.ptvD100,
            "%.2f" % x.ptvD99, "%.2f" % x.bodyV100, "%.2f" % x.bodyV80,
            "%.2f" % x.bodyV50, "%.2f" % x.bodyV30, "%.2f" % x.bodyV10,
            "%.2f" % x.brainPTV_V10, "%.2f" % x.brainPTV_V12]


def indDataLine(x):
    """Read in PTV object, calculate and return indicies data"""
    return [x.ptvName, "%.2f" % x.conformity_index(),
            "%.2f" % x.target_conf_index(),"%.2f" % x.selectivity_index(),
            "%.2f" % x.paddick_index(), "%.2f" % x.gradient_index_80(),
            "%.2f" % x.gradient_index_50(), "%.2f" % x.gradient_index_30(),
            "%.2f" % x.v50_ptv_vol(), "%.2f" % x.brainPTV_V12]


def createPatInfo(dat):
    """Read in PTV object, calculate and return Patient data"""
    return (['Patient Name', dat['name']],
            ['Patient ID', dat['pat_id']],
            ['DOB', dat['dob']],
            ['Site', dat['site']],
            ['Prescription (Gy)', dat['prescription']],
            ['Fractionation (#)', dat['fractionation']],
            ['Dose/# (Gy)', dat['dose_per_fraction']],
            ['Plan Geometry', dat['plan_geometry']])


def createElements(pat_info, ind_data, target_data):
    """Format the tables for alignment, col widths, and add a title
     and line breaks (Spacers). """

    styles = getSampleStyleSheet()
    tabstyle = TableStyle([('GRID', (0, 0), (-1, -1), 0.5)])

    pat_table = Table(pat_info, hAlign='LEFT')
    pat_table.setStyle(tabstyle)

    ind_table = Table(ind_data, hAlign='LEFT', colWidths=columnWidths(ind_data))
    ind_table.setStyle(tabstyle)

    target_table = Table(target_data, hAlign='LEFT')
    target_table.setStyle(tabstyle)

    report_title = Paragraph("SRS Plan Assessment Form", styles["h2"])

    elems = [report_title,Spacer(1, 10),
             pat_table, Spacer(1, 10),
             ind_table, Spacer(1, 10),
             PageBreak(), target_table]
    return elems


def columnWidths(indicies_data):
    """Read in the indicies data to get the number of
     PTVs. Return an array of columns widths, where only
     the text columns (first 3) have set widths.
     'None' for all PTV columns

     TODO: get number of PTVs from indicies_data, so
        return array has the correct number of 'None's

        """
    res = [100, 150, 200, None, None, None, None]
    return res


if __name__ == '__main__':

    filename = "/Users/anil/Downloads/example_json.txt"
    with open(filename) as f:
        data = json.load(f)

    pat_info = createPatInfo(data)
    [ind_data, target_data] = createTables(data)
    doc = SimpleDocTemplate('simple_output.pdf', pagesize=landscape(A4))
    elements = createElements(pat_info, ind_data, target_data)
    doc.build(elements)
