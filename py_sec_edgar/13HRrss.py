# -*- coding: utf-8 -*-
from pprint import pprint
import os, sys
import click
import atoma, requests, json


# sys.path.append(os.path.join(os.getcwd(), os.path.dirname(__file__)))
# sys.path.append(os.path.join(os.getcwd(), os.path.dirname(__file__), 'feeds'))

# import py_sec_edgar.feeds.idx

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import py_sec_edgar.feeds.full_index
# from py_sec_edgar.edgar_filing import SecEdgarFiling
from settings import CONFIG

proxies = {
  "http": None,
  "https": None,
}
headers ={'User-Agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0 '}


def main():

    # ********** Process the 13F rss
    rss_content = atoma.parse_rss_file(os.path.join(CONFIG.REF_DIR, "13F-HR.rss"))
    
    from urllib.parse import urlparse, urljoin
    
    i = 0    
    for item in rss_content.items:
        i = i + 1
        if i < 2 :
            cik_13hr_url = item.link
            cik_13hr_json_url = urljoin(cik_13hr_url, 'index.json')
            cik = urlparse(cik_13hr_url).path.split("/")[2].split('-')[0]
            cik_year = urlparse(cik_13hr_url).path.split("/")[2].split('-')[1]
            cik_assesion = urlparse(cik_13hr_url).path.split("/")[2].split('-')[2]
            cik_dir = os.path.join(CONFIG.SEC_REPORT_13HR_FILING_CIK_DIR, cik, cik_year, cik_assesion)
            cik_index_json_file = os.path.join(cik_dir, 'index.json')
            print(cik_13hr_json_url, cik_dir)
            # cik_index_json = requests.get(cik_13hr_json_url, headers=headers, proxies=proxies) 
            if not os.path.exists(cik_index_json_file): 
                cik_index_response = requests.get(cik_13hr_json_url, headers=headers, proxies=proxies) 
                cik_index_json = cik_index_response.json()
                if not os.path.exists(cik_dir):
                    os.makedirs(cik_dir)

                with open(cik_index_json_file, 'w') as f:
                    json.dump(cik_index_json, f)
            else:
                with open(cik_index_json_file, 'r') as f:
                    cik_index_json = json.load(f)



                # ********** Process the each CIK index json and download the attachments
                # with open(os.path.join(CONFIG.REF_DIR, "13F-HR-index.json")) as f:
                #     index_content = json.load(f)

            # print(cik_index_json)
            for attachment in cik_index_json['directory']['item']:
                if attachment['size'] != "":
                    cik_index_attachment_file = os.path.join(cik_dir, attachment['name'])
                    if not os.path.exists(cik_index_attachment_file): 
                        attachment_file = requests.get(urljoin(cik_13hr_url, attachment['name']), headers=headers, proxies=proxies) 
                        attachment_file_content = attachment_file.content
                        with open(cik_index_attachment_file, 'w') as foutput:
                            foutput.write(attachment_file_content.decode("utf-8") )
                    else:
                        with open(cik_index_attachment_file, 'r') as foutput:
                            attachment_file_content = foutput.read()
                    
                    if attachment['name'] == "primary_doc.xml":
                        from lxml import etree as etree_lxml
                        with open(cik_index_attachment_file, 'r') as foutput:
                            attachment_file_content = etree_lxml.parse(foutput)
                        primary_doc = attachment_file_content.getroot()


                        
                        for chd in primary_doc.getchildren():
                            print(chd.tag)
                            for ch in chd.getchildren():
                                print(ch.tag)
                        ns = {"ff": "http://www.sec.gov/edgar/thirteenffiler"}

                        print(primary_doc.xpath('/headerData', namespaces=ns))


                    

    # py_sec_edgar.feeds.full_index.update_full_index_feed(skip_if_exists=True)

    # df_filings_idx = py_sec_edgar.feeds.idx.load_local_idx_filing_list(ticker_list_filter=ticker_list_filter, form_list_filter=form_list_filter)

    # for i, filing_json in df_filings_idx.iterrows():

    #     pprint(filing_json)

    #     sec_filing = SecEdgarFiling(filing_json)
    #     sec_filing.download()
    #     sec_filing.load()
    #     sec_filing.parse_header(save_output=save_output)
    #     sec_filing.process_filing(save_output=save_output)

if __name__ == "__main__":

    main()
