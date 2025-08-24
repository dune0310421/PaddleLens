import yaml
import json
import os
import logging

def extension_to_language() -> dict:
    '''
    获取扩展名到编程语言的映射
    '''

    if os.path.exists('data/extension_to_language.json'):
        with open('data/extension_to_language.json', 'r', encoding='utf-8') as f:
            ext_to_lang = json.load(f)
        return ext_to_lang

    # 读取文件
    # https://github.com/github/linguist/blob/master/lib/linguist/languages.yml
    try:
        with open('data/languages.yml', 'r', encoding='utf-8') as f:
            lines = "".join(f.readlines()[37:])
    except FileNotFoundError:
        logging.error("languages.yml not found. Please download it from https://github.com/github/linguist/blob/master/lib/linguist/languages.yml")
        return {}
    
    all_lang_info = yaml.load(lines, Loader=yaml.FullLoader)
    all_lang_to_extension = {}
    for language in all_lang_info:
        if "extensions" in all_lang_info[language]:
            all_lang_to_extension[language] = all_lang_info[language]['extensions']
    # print(all_lang_to_extension)

    # 筛选所需要的语言
    langs = ["Python", "C++", "Java", "C", "C#", "JavaScript", "Go", "SQL", "Visual Basic .NET", "Fortran"]  # TIOBE Index，2024年12月版本
    # 添加paddle项目中用到的语言
    with open('data/paddle_repos.json', 'r', encoding='utf-8') as f:
        repos = json.load(f)
    for repo in repos:
        if repo['language'] != None and repo['language'] != 'Jupyter Notebook' and repo['language'] not in langs:
            langs.append(repo['language'])
    # # 添加文档相关语言
    # langs += ["Markdown", "HTML", "CSS", "JSON", "YAML", "XML", "Dockerfile", "Makefile", "TOML"]
    # langs = list(set(langs))  # 去重
    # logging.info(f"Selected languages: {langs}")
    
    # 构造lang -> extension的映射
    lang_to_ext = {}
    for lang in langs:
        if lang in all_lang_to_extension:
            lang_to_ext[lang] = all_lang_to_extension[lang]
        else:
            logging.warning(f"Language {lang} not found in the YAML file. It may not be supported.")
    lang_to_ext['C/C++'] = list(set(lang_to_ext['C']) | set(lang_to_ext['C++']))  # 合并C和C++
    lang_to_ext.pop('C', None)
    lang_to_ext.pop('C++', None)
    lang_to_ext['Python'] += [".ipynb"]  # Python增加.ipynb

    # 互换key和value，构造 extension -> language 的映射
    invalid_extensions = [".h", ".cgi", ".fcgi", ".spec", ".inc"]
    ext_to_lang = {}
    for lang in lang_to_ext:
        for extension in lang_to_ext[lang]:
            if extension in invalid_extensions:
                continue
            ext_to_lang[extension] = lang
    
    with open('data/extension_to_language.json', 'w', encoding='utf-8') as f:
        json.dump(ext_to_lang, f, indent=4, ensure_ascii=False)

    return ext_to_lang

if __name__ == "__main__":

    logging.basicConfig(
        format="%(asctime)s (PID %(process)d) [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)

    result = extension_to_language()
    # print(f"Extension to language mapping: {result}")