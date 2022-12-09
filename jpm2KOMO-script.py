import re # for Regular expressions """
import os

def main():
    """
    Automatically generates a beamer/KOMA-script (scrartcl) presentation draft from an latex article
    Notes:
           - Some functionality has been disabled by comments.
by Septimus G in 2017, and modified by Tex Chi in 2021 at TMU
To use it you can simply run it in the same directory as your article file which should be named main.tex. The output presentation will be written to slides.tex
> python3 jpm2beamer.py main.tex
or 
> rstudio "under conda virtual environment"
https://tex.stackexchange.com/questions/397055/automatically-generating-beamer-presentation-draft-from-article
https://jakevdp.github.io/WhirlwindTourOfPython/14-strings-and-regular-expressions.html

Regular Expressions https://docs.python.org/3/library/re.html#re-syntax
"\d"	Match any digit		"\D"	Match any non-digit
"\s"	Match any whitespace		"\S"	Match any non-whitespace
"\w"	Match any alphanumeric char		"\W"	Match any non-alphanumeric char

repetitions: ? {0, 1}; * {0, inf}; + {1, inf}
    """

    article_file_path = 'main.tex'
    KOMA_file_path = 'keynote0.tex'
    if os.path.isfile(KOMA_file_path):
       os.remove(KOMA_file_path)
    else:
      print("We will create a new output file.")

    written_figures = []
    written_tables = []
    
    with open(article_file_path, 'r') as art:
        with open(KOMA_file_path, 'w') as outf: #auto outf.close()
           # in_frame = False
            for line in art:  # lines = art.readlines() ?

                # Preamble
                #(currently ignoring)

                # Copy header
                # Ignores unnumbered sections
                  # The r preface in r'\$' indicates a raw (or verbatim) string to avoid escape characters by Python
                if line.startswith('\section{') or line.startswith(r'\subsection'):

                 #   if in_frame:
                  #      outf.write(r'\end{frame}'+'\n')
                   #     in_frame = False

                    outf.write('\n' + safe_line(line) + '\n')

                if line.startswith(r'\subsubsection'):
                    outf.write('\n' + '' + safe_line(line) + '\n')
#                if line.startswith(r'\label{'):
#                    outf.write('%%%' + safe_line(line)) # r'%%%\\label{'

                    # Create frame for subsections
               #     if line.startswith(r'\subsection'):
                #        outf.write(r'\begin{frame}{\secname: \subsecname}'+'\n')
                 #       in_frame = True

                # Insert figure environment at their \ref{} section of main.tex
                # *** check the "~" of Figure~\ref{}; and add "x\ref{}" to commented
                fig_refs = re.findall(r'~\\ref{fig:([\w\d -_]+)}', line) #  () group for all \ref{} in one paragraph
                if fig_refs:
                    for fig_ref in fig_refs:
                        if fig_ref not in written_figures:
                            fig_frame = safe_line(find_fig_str(article_file_path, fig_ref))
                            outf.write(fig_frame)
                            written_figures.append(fig_ref)
                            
                # Insert table environment at their \ref{} section of main.tex
                # *** check the "~" of Table~\ref{}; and add "x\ref{}" to commented
                tab_refs = re.findall(r'~\\ref{tab([\w\d -_:]+)}', line) #  () group for all \ref{} in one paragraph
                if tab_refs:
                    for tab_ref in tab_refs:
                        if tab_ref not in written_tables:
                            tab_frame = safe_line(find_tab_str(article_file_path, tab_ref))
                            outf.write(tab_frame)
                            written_tables.append(tab_ref)

            #if in_frame:
             #   outf.write(r'\end{frame}' + '\n')
              #  in_frame = False
    #art.close()
    #outf.close()
    # end of main() declairation

def safe_line(line):
    """ Processes latex control sequences which cause beamer to break
     * Remove x\label{}, \todo{}
     * Add \protect infront of \textit{}
    """
    sline = line
#    sline = re.sub(r'\\label{[\w\d:\s]+}', '', sline) # 
    sline = re.sub(r'\\todo{[\w\d:\s]+}', '', sline)

    sline = re.sub(r'\\textit{', r'\\protect\\textit{', sline)
    return sline

def find_fig_str(text_file_path, fig_ref):
    """ Finds the figure floating environment based on label
    """
    with open(text_file_path, 'r') as tfile:
        envstr = ''
        in_fig = False
        for line in tfile:

            if line.startswith(r"\begin{figure}"):
                in_fig = True

            if in_fig:
                to_write = line
                # add placement specifications [ht], and \floatbox for presentation in KOMO-script:
                if line.startswith(r"\begin{figure}"):
                    to_write = re.sub(r'\[([\w]+)\]', r'[ht]', line) + '\n' + '\\floatbox[{\\capbeside\\thisfloatsetup{capbesideposition={right,center},capbesidewidth=.35\\linewidth,capbesidesep=quad}}]{figure}[\\FBwidth]' + '\n'
                # comment label
                # if line.startswith(r'\label{'):   # 7 \label in main.tex
                if re.match(r'[\t\s]?\\label{fig:',line):  # [\t\s]?
                    to_write = r'%%%' + line
                # add \caption to make it fill the whole slide {} under \floatbox
                         # '{\caption{...}}' + '\n' + 
                if re.match(r'[\t\s]?\\caption',line): # [b]?caption for \floatbox
                    to_write = '{\captionsetup{labelformat=empty} ' + line + '} \n'
                if re.match(r'[\t\s]?\\bcaption',line): # for \floatbox
                    to_write = '*** check *** {' + re.sub(r'bcaption',r'caption',line) + '} \n'
                # replace figure width to make it fill the whole slide                         
                         # '{\includegraphics{...}}' + '\n' + 
                if re.match(r'[\t\s]?\\includegraphics',line):
                    to_write = '{' + re.sub(r'\[([\w=\d]+)\]', r'[width =\\textwidth, height = 0.6\\textheight, keepaspectratio]', line) + '} \n'

                envstr += to_write

            labelmatch = re.match(r'[\t\s]?\\label{fig:([\w\d -_]+)}',line)
            # a match only at the beginning of the string
            if labelmatch:
                if labelmatch.group(1) == fig_ref:
                    right_fig = True
                else:
                    right_fig = False

            if line.startswith(r"\end{figure}"):
                in_fig = False
                envstr += '\n'
                if right_fig: # Stop searching
                    break
                else:
                    envstr = ''
            # end of for loop

    # Make figure be in its own figure:
#    if envstr: # with \begin{figure}, \end{figure}
       # envstr = r'\begin{frame}{\subsecname}' + '\n' + envstr + r'\end{frame}' + '\n'
#        envstr = envstr + '\n' + r'\end{figure}' + '\n'
    return envstr



def find_tab_str(text_file_path, tab_ref): # specialtable or table
    """ Finds the tables floating environment based on label
    """
    with open(text_file_path, 'r') as tfile:
        envstr = ''
        in_fig = False
        for line in tfile:

            if line.startswith(r"\begin{specialtable}"):
                in_fig = True

            if in_fig:
                to_write = line
                # add placement specifications [ht], and \floatbox for presentation in KOMO-script:
#                if line.startswith(r"\begin{figure}"):
#                    to_write = re.sub(r'\[([\w]+)\]', r'[ht]', line) + '\n' + r'\\floatbox[{\\capbeside\\thisfloatsetup{capbesideposition={right,center},capbesidewidth=.35\\linewidth,capbesidesep=quad}}]{figure}[\\FBwidth]' + '\n'
                # comment label
                # if line.startswith(r'\label{'):   # 7 \label in main.tex
                if re.match(r'[\t\s]?\\label{tab',line):  # [\t\s]?
                    to_write = r'%%%' + line
                # add \caption to make it fill the whole slide {} under \floatbox
                         # '{\caption{...}}' + '\n' + 
                if re.match(r'[\t\s]?\\[b]?caption',line): # [b]?caption for \floatbox
                    to_write = '%%%' + line + '\n'
#                if re.match(r'[\t\s]?\\bcaption',line): # for \floatbox
#                    to_write = '*** check *** {' + re.sub(r'bcaption',r'caption',line) + '} \n'
                # replace figure width to make it fill the whole slide                         
                         # '{\includegraphics{...}}' + '\n' + 
#                if re.match(r'[\t\s]?\\includegraphics',line):
#                    to_write = '{' + re.sub(r'\[([\w=\d]+)\]', r'[width =\\textwidth, height = 0.6\\textheight, keepaspectratio]', line) + '} \n'

                envstr += to_write

            labelmatch = re.match(r'[\t\s]?\\label{tab([\w\d -_:]+)}',line)
            # a match only at the beginning of the string
            if labelmatch:
                if labelmatch.group(1) == tab_ref:
                    right_fig = True
                else:
                    right_fig = False

            if line.startswith(r"\end{specialtable}"):
                in_fig = False
                envstr += '\n'
                if right_fig: # Stop searching
                    break
                else:
                    envstr = ''
            # end of for loop

    # Make figure be in its own figure:
#    if envstr: # with \begin{figure}, \end{figure}
       # envstr = r'\begin{frame}{\subsecname}' + '\n' + envstr + r'\end{frame}' + '\n'
#        envstr = envstr + '\n' + r'\end{figure}' + '\n'
    return envstr


main()
