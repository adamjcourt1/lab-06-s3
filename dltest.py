def download_books(list_file, dest_dir):
    path_list = []
    #os.makedirs(dest_dir, exist_ok=True)
    with open(list_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
    for line in lines:
        fname = line.split('/')[-1]
        print(f'Line data: {line}.\nFile name: {fname}')
        '''path = os.path.join(dest_dir, fname)
        if not os.path.exists(path):
            try:
                response = requests.get(line, timeout=30)
                time.sleep(1)
                with open(path, 'w') as f:
                    f.write(response.text)
                    log.info(f'Written file {fname}.')
            except requests.RequestException as e:
                log.info(f'Retrieval from url {line} failed. {e}')
        else:
            log.info(f'File {fname} already present in {dest_dir}. Skipping...')
        path_list.append(path)'''
    return path_list

download_books('book_urls.txt', 0)