#coding:utf-8
import json
import re
import sys,os
from subprocess import PIPE, Popen
from queue import Queue
from threading import Thread
import requests
from bs4 import BeautifulSoup
import urwid
import webbrowser
from urwid.widget import (BOX, FLOW, FIXED)
SO_URL = "https://so.csdn.net/so/search/s.do?q="

# ASCII color codes
GREEN = '\033[92m'
GRAY = '\033[90m'
CYAN = '\033[36m'
RED = '\033[31m'
YELLOW = '\033[33m'
END = '\033[0m'
UNDERLINE = '\033[4m'
BOLD = '\033[1m'

# Scroll actions
SCROLL_LINE_UP = "line up"
SCROLL_LINE_DOWN = "line down"
SCROLL_PAGE_UP = "page up"
SCROLL_PAGE_DOWN = "page down"
SCROLL_TO_TOP = "to top"
SCROLL_TO_END = "to end"

# Scrollbar positions
SCROLLBAR_LEFT = "left"
SCROLLBAR_RIGHT = "right"

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
}


"""
主函数
"""
def main():
    if len(sys.argv) == 1 or sys.argv[1].lower() == "-h" or sys.argv[1].lower() == "--help":
        print("hello")
    elif sys.argv[1].lower() == "-q" or sys.argv[1].lower() == "--query":
        print("ok")
    else:
        #调用get_language（）函数得到编程语言
        language = get_language(sys.argv[1].lower())
        #得到文件名称
        file_path = sys.argv[1:]
        #print(file_path)
        #执行execute()函数,得到被执行代码的程序错误信息
        output, error = execute([language] + file_path)
        #获取程序报错提示
        error_msg = get_error_message(error, language)
    
        if error_msg != None:
            query = "%s+%s" % (language, error_msg)
            #print(query)
            #将错误提示作为参数，进行爬取CSDN相关帖子
            #a = input("选择1.CSDN/2.简书？（1 or 2）？")
            #if a ==str(1):
            search_results,captcha = parser_csdn(query)
            #print(captcha)
            if search_results != []:
                if captcha:
                    print("\n%s%s%s" % (RED, "对不起，CSDN暂时不能请求，请过一分钟再次尝试！\n", END))
                    return
                elif confirm("\n是否需要在CSDN上搜索结果?"):
                    App(search_results) # Opens interface
                else:
                    print("\n%s%s%s" % (RED, "关闭使用！\n", END))
            #else:
                #parser_js(query)
        else:
            print("文件无错误！")

"""
提示输入关键字所代表的bool值
"""     
def confirm(question):
    """Prompts a given question and handles user input."""
    valid = {"yes": True, 'y': True, "ye": True,
             "no": False, 'n': False, '': True}
    prompt = " [Y/n] "

    while True:
        print(BOLD + CYAN + question + prompt + END)
        choice = input().lower()
        if choice in valid:
            return valid[choice]

        print("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")                    


"""
爬取CSDN博客，得到解决问题的相关帖子，并返回标题和超链接

"""
def parser_csdn(query):

    search_results = []
    for x in range(1,6):
        url = "https://so.csdn.net/so/search/s.do?p="+str(x)+"&q="+str(query)+"&t=blog&u="
        html = requests.get(url,headers = headers)
        html.encoding = "utf-8"
        r = html.text
        soup = BeautifulSoup(r,"html.parser")
        for Result in soup.find_all("dl",class_="search-list J_search"):
            for j in Result.find_all('dt'):
                for a in j.find_all('a'):
                    t = a.get_text()
                    h = a["href"]
                    if "CSDN" not in t:
                        title_container = t
                        title_href = h
                all_red = 0
                for em in j.find_all('em'):
                    red = len(em.get_text())
                    all_red = red+all_red

                        #print(title_container)
                        #print(title_href)
            for fr in Result.find_all('span',class_='down fr'):
                read = fr.get_text()
            
     

            search_results.append({
                "Title":title_container,
                        "read_data":read[:-3],
                        "red":all_red,
                        "URL":title_href
                })

        soup = souper(title_href)
    
    


    #search_results = sorted(search_results,key=lambda search_results:search_results[1])
    #print(search_results)
    
    search_results = sorted(search_results, key=lambda dic : int(int(dic['read_data'])+int(dic['red']*1000)),reverse=True)

        #print(search_results)
    #search_results =  select_sort(search_results)  
    #print(search_results)
    return (search_results, False)


def parser_js(query):
    headers= {
        "cookie":"__yadk_uid=bDwCioPnl9z3BNoIkNaF5pFntBBiWDxf; read_mode=day; default_font=font2; locale=zh-CN; _m7e_session_core=4bd2e7ed5b68a133cf6e8f9586cbcfd5; Hm_lvt_0c0e9d9b1e7d617b3e6842e85b9fb068=1555321708,1555321765,1555321841,1555334141; Hm_lpvt_0c0e9d9b1e7d617b3e6842e85b9fb068=1555334338; signin_redirect=https%3A%2F%2Fwww.jianshu.com%2Fsearch%3Fq%3DIndexError%253A%2520list%2520index%2520out%2520of%2520range%26page%3D1%26type%3Dnote; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2216a1b1a8218cef-0bac544d2ce1b1-18211c0a-2073600-16a1b1a8219551%22%2C%22%24device_id%22%3A%2216a1b1a8218cef-0bac544d2ce1b1-18211c0a-2073600-16a1b1a8219551%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D",
        "user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
    }
    search_results = []
    session  = requests.session()
    for x in range(1,4):
        url = "https://www.jianshu.com/search?q="+str(query)+"type=note&page="+str(x)+"&order_by=default"
        payload = {
            "q":"IndexError: list index out of range",
            "type":"note",
            "page":x,
            "order_by":"default"
        }
        html = requests.post(url,headers = headers,data=payload)
        html.encoding = "utf-8"
        r = html.text
        #json = json.dumps(r)
        print(r)
        soup = BeautifulSoup(r,"html.parser")
        note_list = soup.find_all("div",class_="search-content")
        #print(note_list)
        #for j in note_list.find_all('li'):
            #for a in j.find_all('a',class_='title'):
            #    t = a.get_text()
            #    h = a["href"]
            #    print(t)
            #        print(h)
           
               
           



"""
解析enter进入后的文本信息
"""
def souper(title_href):
    """Turns a given URL into a BeautifulSoup object."""

    try:
        html = requests.get(title_href, headers=headers)
    except requests.exceptions.RequestException:
        sys.stdout.write("\n%s%s%s" % (RED, "Rebound was unable to fetch Stack Overflow results. "
                                            "Please check that you are connected to the internet.\n", END))
        sys.exit(1)

    if re.search("\.com/nocaptcha", html.url): # URL is a captcha page
        return None
    else:
        return BeautifulSoup(html.text, "html.parser")
        



"""
获取执行的代码文件的编程语言
"""
def get_language(file_path):
    """Returns the language a file is written in."""
    if file_path.endswith(".py"):
        return "python3"
    elif file_path.endswith(".js"):
        return "node"
    elif file_path.endswith(".go"):
        return "go run"
    elif file_path.endswith(".rb"):
        return "ruby"
    elif file_path.endswith(".java"):
        return 'javac' # Compile Java Source File
    elif file_path.endswith(".class"):
        return 'java' # Run Java Class File
    else:
        return '' # Unknown language


"""
调用模块subprocess，程序产生一个子进程

"""
def read(pipe, funcs):
    """Reads and pushes piped output to a shared queue and appropriate lists."""
    for line in iter(pipe.readline, b''):
        for func in funcs:
            func(line.decode("utf-8"))
    pipe.close()


def write(get):
    """Pulls output from shared queue and prints to terminal."""
    for line in iter(get, None):
        print(line)



def execute(command):
    """Executes a given command and clones stdout/err to both variables and the
    terminal (in real-time)."""
    process = Popen(
        command,
        cwd=None,
        shell=False,
        close_fds=True,
        stdout=PIPE,
        stderr=PIPE,
        bufsize=1
    )

    output, errors = [], []
    pipe_queue = Queue()

    # Threads for reading stdout and stderr pipes and pushing to a shared queue
    stdout_thread = Thread(target=read, args=(process.stdout, [pipe_queue.put, output.append]))
    stderr_thread = Thread(target=read, args=(process.stderr, [pipe_queue.put, errors.append]))

    writer_thread = Thread(target=write, args=(pipe_queue.get,)) # Thread for printing items in the queue

    # 产生每个线程
    for thread in (stdout_thread, stderr_thread, writer_thread):
        thread.daemon = True
        thread.start()

    process.wait()

    for thread in (stdout_thread, stderr_thread):
        thread.join()

    pipe_queue.put(None)

    output = ' '.join(output)
    errors = ' '.join(errors)

    if "java" != command[0] and not os.path.isfile(command[1]): # File doesn't exist, for java, command[1] is a class name instead of a file
        return (None, None)
    else:
        return (output, errors)

"""
获取错误信息
"""
def get_error_message(error, language):
    """Filters the stack trace from stderr and returns only the error message."""
    if error == '':
        return None
    elif language == "python3":
        if any(e in error for e in ["KeyboardInterrupt", "SystemExit", "GeneratorExit"]): # Non-compiler errors
            return None
        else:
            return error.split('\n')[-2].strip()
    elif language == "node":
        return error.split('\n')[4][1:]
    elif language == "go run":
        return error.split('\n')[1].split(": ", 1)[1][1:]
    elif language == "ruby":
        error_message = error.split('\n')[0]
        return error_message[error_message.rfind(": ") + 2:]
    elif language == "javac":
        m = re.search(r'.*error:(.*)', error.split('\n')[0])
        return m.group(1) if m else None
    elif language == "java":
        for line in error.split('\n'):
            # Multiple error formats
            m = re.search(r'.*(Exception|Error):(.*)', line)
            if m and m.group(2):
                return m.group(2)

            m = re.search(r'Exception in thread ".*" (.*)', line)
            if m and m.group(1):
                return m.group(1)

        return None
"""
调用urwid库，来设计终端命令行操作界面
"""
class App(object):
    def __init__(self, search_results):
        self.search_results, self.viewing_answers = search_results, False
        self.palette = [
            ("title", "light cyan,bold", "default", "standout"),
            ("stats", "light green", "default", "standout"),
            ("menu", "black", "light cyan", "standout"),
            ("reveal focus", "black", "light cyan", "standout"),
            ("no answers", "light red", "default", "standout"),
            ("code", "brown", "default", "standout")
        ]
        self.menu = urwid.Text([
            u'\n',
            ("menu", u" ENTER "), ("light gray", u" 查看帖子"),
            ("menu", u" B "), ("light gray", u" 打开浏览器 "),
            ("menu", u" Q "), ("light gray", u" 退出"),
        ])

        results = list(map(lambda result: urwid.AttrMap(SelectableText(self._stylize_title(result)), None, "reveal focus"), self.search_results)) # TODO: Add a wrap='clip' attribute
        content = urwid.SimpleListWalker(results)
        self.content_container = urwid.ListBox(content)
        layout = urwid.Frame(body=self.content_container, footer=self.menu)

        self.main_loop = urwid.MainLoop(layout, self.palette, unhandled_input=self._handle_input)
        self.original_widget = self.main_loop.widget

        self.main_loop.run()


    def _handle_input(self, input):
        if input == "enter": # View answers
            url = self._get_selected_link()


            if url != None:
                self.viewing_answers = True
                question_title,question_desc,question_stats,answers = get_question_and_answers(url)
                #raise urwid.ExitMainLoop()
                #print("????")

                #answers =  self._stylize_question(question_title, question_desc,question_stats)
                pile = urwid.Pile([urwid.Text(str(answers))])
                padding = ScrollBar(Scrollable(urwid.Padding(pile, left=3, right=3)))
                filler = urwid.Filler(padding, valign="top")
                linebox = urwid.LineBox(padding)

                menu = urwid.Text([
                    u'\n',
                    ("menu", u" ESC "), ("light gray", u" 返回 "),
                    ("menu", u" B "), ("light gray", u" 打开浏览器 "),
                    ("menu", u" Q "), ("light gray", u" 退出"),
                ])
            

                self.main_loop.widget = urwid.Frame(body=urwid.Overlay(linebox, self.content_container, "center", ("relative", 60), "middle", 23), footer=menu)
        elif input in ('b', 'B'): # Open link
            url = self._get_selected_link()

            if url != None:
                webbrowser.open(url)
        elif input == "esc": # Close window
            if self.viewing_answers:
                self.main_loop.widget = self.original_widget
                self.viewing_answers = False
            else:
                raise urwid.ExitMainLoop()
        elif input in ('q', 'Q'): # Quit
            raise urwid.ExitMainLoop()


    def _get_selected_link(self):
        focus_widget, idx = self.content_container.get_focus() # Gets selected item
        title = focus_widget.base_widget.text

        for result in self.search_results:
            if title == self._stylize_title(result): # Found selected title's search_result dict
                return result["URL"]


    def _stylize_title(self, search_result):
        i = 1
        if i==1:
        #search_result["Answers"] == 1:
            return "%s (%s 次阅读)" % (search_result["Title"], search_result["read_data"])
            


    def _stylize_question(self, title, desc, stats):
        new_title = urwid.Text(("title", u"%s" % title))
        new_stats = urwid.Text(("stats", u"%s\n" % stats))

        return [new_title, desc, new_stats]

class SelectableText(urwid.Text):
    def selectable(self):
        return True


    def keypress(self, size, key):
        return key


def get_question_and_answers(url):
    html = requests.get(url,headers = headers)
    html.encoding = "utf-8"
    r = html.text
    soup = BeautifulSoup(r,"html.parser")
    question_title = soup.find_all("div",class_="article-title-box")
    for i in question_title:
        question_title = i.get_text()
    question_desc = soup.find_all("span",class_="time")
    for j in question_desc:
        question_desc = j.get_text()
    question_stats = soup.find_all("div",attrs={"article":"baidu_pl"})
    for k in question_stats:
        question_stats = k.get_text()
    answers = soup.find_all("div",class_="blog-content-box")
    if answers:
        for n in answers:
            answers = n.get_text()
    else:
        answers = "空！"
    
    return question_title,question_desc,question_stats,answers


    


class ScrollBar(urwid.WidgetDecoration):
    # TODO: Change scrollbar size and color(?)

    def sizing(self):
        return frozenset((BOX,))


    def selectable(self):
        return True


    def __init__(self, widget, thumb_char=u'\u2588', trough_char=' ',
                 side=SCROLLBAR_RIGHT, width=1):
        """Box widget that adds a scrollbar to `widget`."""
        self.__super.__init__(widget)
        self._thumb_char = thumb_char
        self._trough_char = trough_char
        self.scrollbar_side = side
        self.scrollbar_width = max(1, width)
        self._original_widget_size = (0, 0)
        self._dragging = False


    def render(self, size, focus=False):
        maxcol, maxrow = size

        ow = self._original_widget
        ow_base = self.scrolling_base_widget
        ow_rows_max = ow_base.rows_max(size, focus)
        if ow_rows_max <= maxrow: # Canvas fits without scrolling - no scrollbar needed
            self._original_widget_size = size
            return ow.render(size, focus)

        sb_width = self._scrollbar_width
        self._original_widget_size = ow_size = (maxcol-sb_width, maxrow)
        ow_canv = ow.render(ow_size, focus)

        pos = ow_base.get_scrollpos(ow_size, focus)
        posmax = ow_rows_max - maxrow

        # Thumb shrinks/grows according to the ratio of
        # <number of visible lines> / <number of total lines>
        thumb_weight = min(1, maxrow / max(1, ow_rows_max))
        thumb_height = max(1, round(thumb_weight * maxrow))

        # Thumb may only touch top/bottom if the first/last row is visible
        top_weight = float(pos) / max(1, posmax)
        top_height = int((maxrow-thumb_height) * top_weight)
        if top_height == 0 and top_weight > 0:
            top_height = 1

        # Bottom part is remaining space
        bottom_height = maxrow - thumb_height - top_height
        assert thumb_height + top_height + bottom_height == maxrow

        # Create scrollbar canvas
        top = urwid.SolidCanvas(self._trough_char, sb_width, top_height)
        thumb = urwid.SolidCanvas(self._thumb_char, sb_width, thumb_height)
        bottom = urwid.SolidCanvas(self._trough_char, sb_width, bottom_height)
        sb_canv = urwid.CanvasCombine([
            (top, None, False),
            (thumb, None, False),
            (bottom, None, False),
        ])

        combinelist = [(ow_canv, None, True, ow_size[0]), (sb_canv, None, False, sb_width)]
        if self._scrollbar_side != SCROLLBAR_LEFT:
            return urwid.CanvasJoin(combinelist)
        else:
            return urwid.CanvasJoin(reversed(combinelist))


    @property
    def scrollbar_width(self):
        return max(1, self._scrollbar_width)


    @scrollbar_width.setter
    def scrollbar_width(self, width):
        self._scrollbar_width = max(1, int(width))
        self._invalidate()


    @property
    def scrollbar_side(self):
        return self._scrollbar_side


    @scrollbar_side.setter
    def scrollbar_side(self, side):
        if side not in (SCROLLBAR_LEFT, SCROLLBAR_RIGHT):
            raise ValueError("scrollbar_side must be 'left' or 'right', not %r" % side)
        self._scrollbar_side = side
        self._invalidate()


    @property
    def scrolling_base_widget(self):
        """Nearest `base_widget` that is compatible with the scrolling API."""
        def orig_iter(w):
            while hasattr(w, "original_widget"):
                w = w.original_widget
                yield w
            yield w

        def is_scrolling_widget(w):
            return hasattr(w, "get_scrollpos") and hasattr(w, "rows_max")

        for w in orig_iter(self):
            if is_scrolling_widget(w):
                return w

    @property
    def scrollbar_column(self):
        if self.scrollbar_side == SCROLLBAR_LEFT:
            return 0
        if self.scrollbar_side == SCROLLBAR_RIGHT:
            return self._original_widget_size[0]

    def keypress(self, size, key):
        return self._original_widget.keypress(self._original_widget_size, key)


    def mouse_event(self, size, event, button, col, row, focus):
        ow = self._original_widget
        ow_size = self._original_widget_size
        handled = False
        if hasattr(ow, "mouse_event"):
            handled = ow.mouse_event(ow_size, event, button, col, row, focus)

        if not handled and hasattr(ow, "set_scrollpos"):
            if button == 4: # Scroll wheel up
                pos = ow.get_scrollpos(ow_size)
                if pos > 0:
                    ow.set_scrollpos(pos - 1)
                    return True
            elif button == 5: # Scroll wheel down
                pos = ow.get_scrollpos(ow_size)
                ow.set_scrollpos(pos + 1)
                return True
            elif col == self.scrollbar_column:
                ow.set_scrollpos(int(row*ow.scroll_ratio))
                if event == "mouse press":
                    self._dragging = True
                elif event == "mouse release":
                    self._dragging = False
            elif self._dragging:
                ow.set_scrollpos(int(row*ow.scroll_ratio))
                if event == "mouse release":
                    self._dragging = False



        return False


class Scrollable(urwid.WidgetDecoration):
    # TODO: Fix scrolling behavior (works with up/down keys, not with cursor)

    def sizing(self):
        return frozenset([BOX,])


    def selectable(self):
        return True


    def __init__(self, widget):
        """Box widget (wrapper) that makes a fixed or flow widget vertically scrollable."""
        self._trim_top = 0
        self._scroll_action = None
        self._forward_keypress = None
        self._old_cursor_coords = None
        self._rows_max_cached = 0
        self._rows_max_displayable = 0
        self.__super.__init__(widget)


    def render(self, size, focus=False):
        maxcol, maxrow = size

        # Render complete original widget
        ow = self._original_widget
        ow_size = self._get_original_widget_size(size)
        canv = urwid.CompositeCanvas(ow.render(ow_size, focus))
        canv_cols, canv_rows = canv.cols(), canv.rows()

        if canv_cols <= maxcol:
            pad_width = maxcol - canv_cols
            if pad_width > 0: # Canvas is narrower than available horizontal space
                canv.pad_trim_left_right(0, pad_width)

        if canv_rows <= maxrow:
            fill_height = maxrow - canv_rows
            if fill_height > 0: # Canvas is lower than available vertical space
                canv.pad_trim_top_bottom(0, fill_height)
        self._rows_max_displayable = maxrow
        if canv_cols <= maxcol and canv_rows <= maxrow: # Canvas is small enough to fit without trimming
            return canv

        self._adjust_trim_top(canv, size)

        # Trim canvas if necessary
        trim_top = self._trim_top
        trim_end = canv_rows - maxrow - trim_top
        trim_right = canv_cols - maxcol
        if trim_top > 0:
            canv.trim(trim_top)
        if trim_end > 0:
            canv.trim_end(trim_end)
        if trim_right > 0:
            canv.pad_trim_left_right(0, -trim_right)

        # Disable cursor display if cursor is outside of visible canvas parts
        if canv.cursor is not None:
            curscol, cursrow = canv.cursor
            if cursrow >= maxrow or cursrow < 0:
                canv.cursor = None

        # Let keypress() know if original_widget should get keys
        self._forward_keypress = bool(canv.cursor)

        return canv


    def keypress(self, size, key):
        if self._forward_keypress:
            ow = self._original_widget
            ow_size = self._get_original_widget_size(size)

            # Remember previous cursor position if possible
            if hasattr(ow, "get_cursor_coords"):
                self._old_cursor_coords = ow.get_cursor_coords(ow_size)

            key = ow.keypress(ow_size, key)
            if key is None:
                return None

        # Handle up/down, page up/down, etc
        command_map = self._command_map
        if command_map[key] == urwid.CURSOR_UP:
            self._scroll_action = SCROLL_LINE_UP
        elif command_map[key] == urwid.CURSOR_DOWN:
            self._scroll_action = SCROLL_LINE_DOWN
        elif command_map[key] == urwid.CURSOR_PAGE_UP:
            self._scroll_action = SCROLL_PAGE_UP
        elif command_map[key] == urwid.CURSOR_PAGE_DOWN:
            self._scroll_action = SCROLL_PAGE_DOWN
        elif command_map[key] == urwid.CURSOR_MAX_LEFT: # "home"
            self._scroll_action = SCROLL_TO_TOP
        elif command_map[key] == urwid.CURSOR_MAX_RIGHT: # "end"
            self._scroll_action = SCROLL_TO_END
        else:
            return key

        self._invalidate()


    def mouse_event(self, size, event, button, col, row, focus):
        ow = self._original_widget
        if hasattr(ow, "mouse_event"):
            ow_size = self._get_original_widget_size(size)
            row += self._trim_top
            return ow.mouse_event(ow_size, event, button, col, row, focus)
        else:
            return False


    def _adjust_trim_top(self, canv, size):
        """Adjust self._trim_top according to self._scroll_action"""
        action = self._scroll_action
        self._scroll_action = None

        maxcol, maxrow = size
        trim_top = self._trim_top
        canv_rows = canv.rows()

        if trim_top < 0:
            # Negative trim_top values use bottom of canvas as reference
            trim_top = canv_rows - maxrow + trim_top + 1

        if canv_rows <= maxrow:
            self._trim_top = 0  # Reset scroll position
            return

        def ensure_bounds(new_trim_top):
            return max(0, min(canv_rows - maxrow, new_trim_top))

        if action == SCROLL_LINE_UP:
            self._trim_top = ensure_bounds(trim_top - 1)
        elif action == SCROLL_LINE_DOWN:
            self._trim_top = ensure_bounds(trim_top + 1)
        elif action == SCROLL_PAGE_UP:
            self._trim_top = ensure_bounds(trim_top - maxrow+1)
        elif action == SCROLL_PAGE_DOWN:
            self._trim_top = ensure_bounds(trim_top + maxrow-1)
        elif action == SCROLL_TO_TOP:
            self._trim_top = 0
        elif action == SCROLL_TO_END:
            self._trim_top = canv_rows - maxrow
        else:
            self._trim_top = ensure_bounds(trim_top)

        if self._old_cursor_coords is not None and self._old_cursor_coords != canv.cursor:
            self._old_cursor_coords = None
            curscol, cursrow = canv.cursor
            if cursrow < self._trim_top:
                self._trim_top = cursrow
            elif cursrow >= self._trim_top + maxrow:
                self._trim_top = max(0, cursrow - maxrow + 1)


    def _get_original_widget_size(self, size):
        ow = self._original_widget
        sizing = ow.sizing()
        if FIXED in sizing:
            return ()
        elif FLOW in sizing:
            return (size[0],)


    def get_scrollpos(self, size=None, focus=False):
        return self._trim_top


    def set_scrollpos(self, position):
        self._trim_top = int(position)
        self._invalidate()


    def rows_max(self, size=None, focus=False):
        if size is not None:
            ow = self._original_widget
            ow_size = self._get_original_widget_size(size)
            sizing = ow.sizing()
            if FIXED in sizing:
                self._rows_max_cached = ow.pack(ow_size, focus)[1]
            elif FLOW in sizing:
                self._rows_max_cached = ow.rows(ow_size, focus)
            else:
                raise RuntimeError("Not a flow/box widget: %r" % self._original_widget)
        return self._rows_max_cached

    @property
    def scroll_ratio(self):
        return self._rows_max_cached / self._rows_max_displayable



if __name__ =="__main__":
    main()
