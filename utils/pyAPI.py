import subprocess
import os

def check_woc_module():
    try:
        subprocess.run(["python", "-m", "woc.get_values", "--help"], check=True)
        subprocess.run(["python", "-m", "woc.show_content", "--help"], check=True)
        print("woc.get_values and woc.show_content modules are found.")
    except subprocess.CalledProcessError as e:
        print("Could not find woc modules:", e)
    except Exception as e:
        print("An error occurred:", e)

# 通过命令行运行woc
def execCommand(cmd, input, filemode = False, option = 0):
    '''
        cmd: command, such as c2p
        input: file name or str
        filemode: 1文件模式, 返回dict; 0普通模式, 返回list
        option: 0: getValues; 1:showCNT
    '''
    env = os.environ.copy()     # 获取当前环境变量的副本
    # print(env)

    # 选择命令
    if option == 0:
        if filemode:
            command = f"cat '{input}' | python3 -m woc.get_values {cmd}"
        else:
            command = f"echo '{input}' | python3 -m woc.get_values {cmd}"
    else:
        if filemode:
            command = f"cat '{input}' | python3 -m woc.show_content {cmd}"
        else:
            command = f"echo '{input}' | python3 -m woc.show_content {cmd}"

    resultList = []

    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds = True, env=env)
    
    if filemode:
        try:
            lines = proc.communicate()[0].decode('utf-8').strip().split('\n')
            
            for line in lines:
                values = line.strip().split(';')[1:]
                resultList.extend(values)
                # for value in values:
                #     tmp = value.strip('(').strip(')').split(',')[0].strip('\'')
                #     resultList.append(value)
            return resultList
        except:
            return None
    else:
        try:
            for x in proc.communicate()[0].decode('utf-8').strip().split(';')[1:]:
                resultList.append(x)
            return resultList
        except:
            return None
        
if __name__ == '__main__':

    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # check_woc_module()

    # result = execCommand('a2c', 'Audris Mockus <audris@utk.edu>')
    # result = execCommand('a2P', 'Aurelius84 <liujiezhangbupt@gmail.com>')
    # print(len(result))

    # commits_files = execCommand('c2fbb', './developer_data/cache/cmt_hash.txt', True)
    # commits_files = [file.strip('(').strip(')').split(',')[0].strip('\'') for file in commits_files]
    # print(len(commits_files), commits_files[:2])

    commits_projects = execCommand('c2p', './developer_data/cache/cmt_hash.txt', filemode = True)
    print(len(commits_projects), commits_projects[:2])
    commits_files = execCommand('c2fbb', './developer_data/cache/cmt_hash.txt', filemode = True)