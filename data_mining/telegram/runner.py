from data_mining.telegram.crawler import TGCrawler

if __name__ == "__main__":
    crawler = TGCrawler(group_list=['https://t.me/datasciencejobs',
                                    'https://t.me/jobsineu',
                                    'https://t.me/datajobschannel'])

    for group in crawler.group_list:
        parser_obj = crawler.parse(group)
        df_out = parser_obj[0]
        print(len(df_out), df_out.tail(20))
        title_group = str(parser_obj[1])
        df_out.to_csv(rf"./{title_group}.csv", index=False, encoding='utf-8-sig')