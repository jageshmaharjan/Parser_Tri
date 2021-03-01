import argparse
from tika import parser
import re


def check_duplication(line, previous_line):
    '''
    check duplication for a customer record
    :param line:
    :param previous_line:
    :return: boolean result
    '''
    if line == previous_line:
        return True


def get_cust_details(cust_attr_split, n):
    '''
    Customer Record split parser
    :param cust_attr_split:
    :param n:
    :return:
    '''
    cust_addr = ''
    cust_id = 0
    is_medical = False
    medical_practicner = ''
    for i, attr in enumerate(cust_attr_split):
        if is_medical:
            medical_practicner += ''.join(attr) + ' '
        if i == n:
            cust_addr = attr + ' '
        if i > n and not is_medical:
            try:
                int(attr)
                cust_addr += ''.join(attr)
                cust_id = cust_attr_split[i + 1]
                is_medical = True
            except:
                cust_addr += ''.join(attr)
                cust_addr += ' '
    return cust_id, cust_addr, ' '.join(medical_practicner.split()[1:])


def parse_cust_rec(cust_attr):
    '''
    Customer Record Analyzer
    :param cust_attr:
    :return:
    '''
    cust_attr_split = cust_attr.split()
    try:
        int(cust_attr_split[2])
        cust_name = cust_attr_split[0] + ' ' + cust_attr_split[1]
        c_id, c_addr, med_det = get_cust_details(cust_attr_split, 2)
        return cust_name, c_id, c_addr, med_det
    except:
        cust_name = cust_attr_split[0] + ' ' + cust_attr_split[1] + ' ' + cust_attr_split[2]
        c_id, c_addr, med_det = get_cust_details(cust_attr_split, 3)
        return cust_name, c_id, c_addr, med_det


def exceded_days(args, customers, cost_lines, med_equipment):
    '''
    Filterout the list of customer who exceeded 120 days limit, and write to a file
    :param customers: list of customers
    :param cost_lines: list of cost base line
    :return:
    '''
    # [c.split(" ")[11] for i,c in enumerate(cost_lines) if len(c.split(" "))==13 and c.split(" ")[11]!='0.00']
    for idx,cost in enumerate(cost_lines):
        exceed_120 = cost.split(" ")
        # print(med_equipment[-1].split('-')[1])
        if len(exceed_120) == 13 and exceed_120[11] != '0.00':
            cust_rec = parse_cust_rec(customers[idx].strip())
            # print(cust_rec, med_equipment[-1].split('-')[1])
            print(med_equipment)
            with open(args.result, 'a+') as f:
                f.write(cust_rec[1].strip() + '\t' + cust_rec[0].strip() + '\t'+ med_equipment[idx].split('-')[1] + '\t' + cust_rec[3].strip() + '\t' + exceed_120[11] + '\n')
                # f.write(cust_rec[0] + '\t' + cust_rec[1] + '\t' + cust_rec[2] + '\t' + exceed_120[11] + '\n')
            f.close()
            # print(customers[idx].strip() + '\t' + exceed_120[11])
        if len(exceed_120) != 13:
            # print(customers[idx])
            with open(args.result_err, 'a+') as f:
                f.write(customers[idx])
            f.close()


def j_parser(args):
    '''
    Parser builder for the pdf file
    :param args:
    :return:
    '''
    landmarks = ['HOMEREACH LEWIS CENTERProvider', 'Patient Total', 'Reason']
    with open(args.raw_text, "r") as rt:
        content = rt.readlines()
    content = [l for l in content if l is not '\n']
    total_pages = len([l for l in content if l is not '\n' and  landmarks[0] in l])
    print(total_pages)
    rec_lines = False
    customers = []
    cost_lines = []
    med_equipment = []
    for idx, line in enumerate(content):
        if rec_lines and landmarks[1] not in line:
            if len(customers) != 0 and check_duplication(line, customers[-1]):
                rec_lines = False
                continue
            customers.append(line)
            rec_lines = False
        if landmarks[1] in line:
            if content[idx - 1].strip().split(":")[0] == landmarks[0] == landmarks[0]:
                med_equipment.append(content[idx - 14])
            else:
                med_equipment.append(content[idx - 1])
            cost_lines.append(line)
            rec_lines = True
        if landmarks[0] in line:
            rec_lines = True

    customers = [c for c in customers if landmarks[2] not in c]
    customers.remove(customers[-1])

    exceded_days(args, customers, cost_lines, med_equipment)


def main(args):
    pdf_file_name = args.pdf_file  #"/home/jugs/PycharmProjects/ExperimentalProjects/tri_parser/resoures/marion_unbilledrevenue_report.pdf"
    raw = parser.from_file(pdf_file_name)
    raw_str = raw['content']
    with open(args.raw_text, "w") as fr:
        fr.write(raw_str)
    j_parser(args)


if __name__ == "__main__":
    pars = argparse.ArgumentParser("Argument for your app")
    pars.add_argument("--pdf_file", type=str, help="pdf file to read")
    pars.add_argument('--raw_text', type=str, help="path to raw file")
    pars.add_argument("--result", type=str, help="test.txt file")
    pars.add_argument("--result_err", type=str, help="test_err.txt file")
    args = pars.parse_args()
    main(args)