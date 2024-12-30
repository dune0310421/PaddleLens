import yaml
import pickle
import warnings
import os

warnings.filterwarnings('ignore')

def read_file(file_link):
    if not os.path.exists(file_link):
        print(f"File {file_link} not found.")
        return None
    # return pickle.load(open(file_link, "rb"))
    try:
        with open(file_link, "rb") as file:
            content = pickle.load(file)
            if content is None:
                print(f"The content of the file {file_link} is None.")
            else:
                print(f"Successfully read the file {file_link}.")
            return content
    except Exception as e:
        print(f"An error occurred while reading the file {file_link}: {e}")
        return None

def write_file(file_link, file):
    directory = os.path.dirname(file_link)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(file_link, "wb") as f:
        pickle.dump(file, f)

def getPosifixMap():
    '''
    根据文件后缀，返回对应的语言
    '''
    # https://github.com/github/linguist/blob/master/lib/linguist/languages.yml
    with open('./data/languages.yml', 'r', encoding='utf-8') as f:
        lines = "".join(f.readlines()[37:])
    allLanguangeInfo = yaml.load(lines, Loader=yaml.FullLoader)
    langToExtension = {}
    for language in allLanguangeInfo:
        if "extensions" in allLanguangeInfo[language]:
            langToExtension[language] = allLanguangeInfo[language]['extensions']
    
    # print(langToExtension)
    # TIOBE Index for December 2024
    selectedLangs = ["Python", "C++", "Java", "C", "C#", "JavaScript", "Go", "SQL", "Visual Basic .NET", "Fortran"]
    selectedLangToExtension = {}
    for lang in selectedLangs:
        selectedLangToExtension[lang] = langToExtension[lang]
    
    # 将C/C++合并到一起
    selectedLangToExtension['C/C++'] = list(set(selectedLangToExtension['C']) | set(selectedLangToExtension['C++']))
    # Python .ipynb增加
    selectedLangToExtension['Python'] += [".ipynb"]

    del selectedLangToExtension['C']
    del selectedLangToExtension['C++']
    invalidExtensions = [".h", ".cgi", ".fcgi", ".spec", ".inc"]
    # 将key和value换一下，以后缀为key
    extensionToLang = {}
    for lang in selectedLangToExtension:
        for extension in selectedLangToExtension[lang]:
            if extension in invalidExtensions:
                continue
            extensionToLang[extension] = lang 
    # print(extensionToLang)
    write_file('./cache/language.cache',extensionToLang)

if __name__ == '__main__':

    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    getPosifixMap()