import re, os

"""
USAGE:

    Put this .py file in your caseroot and edit .case.run as follows: 
    
    
    REPLACE
    
###############################################################################
def _main_func(description):
###############################################################################
    sys.argv.extend([] if "ARGS_FOR_SCRIPT" not in os.environ else os.environ["ARGS_FOR_SCRIPT"].split())

    caseroot, skip_pnl, set_continue_run, resubmit = parse_command_line(sys.argv, description)
    with Case(caseroot, read_only=False) as case:
        success = case.case_run(skip_pnl=skip_pnl, set_continue_run=set_continue_run, submit_resubmits=resubmit)

    sys.exit(0 if success else 1)
    
    
    
    WITH 
    
###############################################################################
def _main_func(description):
###############################################################################
    sys.argv.extend([] if "ARGS_FOR_SCRIPT" not in os.environ else os.environ["ARGS_FOR_SCRIPT"].split())

    from update_FW_file_pointers import *
    
    caseroot, skip_pnl, set_continue_run, resubmit = parse_command_line(sys.argv, description)
    with Case(caseroot, read_only=False) as case:
        year = current_year_in_case(case)
        update_user_nl_pop(year)
        success = case.case_run(skip_pnl=skip_pnl, set_continue_run=set_continue_run, submit_resubmits=resubmit)
        
    sys.exit(0 if success else 1)
    
    
    
"""


def current_year_in_case(case):
    """
    Function to detect the current simulation year from a case
    For a restart run, it will look for a file path in rpointer.drv
    """
    restart = case.get_value('CONTINUE_RUN')

    if restart:
        rpointer_fname = os.path.join(case.get_value('RUNDIR'), 'rpointer.drv')

        with open(rpointer_fname) as f:
            lines = f.readline()
            year = lines.split('.cpl.r.')[1][0:4]

    else:
        if case.get_value('RUN_TYPE') == 'branch':
            year = case.get_value('RUN_REFDATE')[0:4]
        else:
            # Startup or hybrid
            year = case.get_value('RUN_STARTDATE')[0:4]
    return int(year)


def update_user_nl_pop(year, fname = 'user_nl_pop'):
    replaced_content = ""

    with open(fname) as f:

        pattern = re.compile(r'[0-9]{4}.nc')    

        for line in f:
            line_nw = "".join(line.split()) # removes white space

            if (line_nw.find('imau_filename=') != -1):
                out = re.sub(pattern, '{}.nc'.format(year), line) 
            elif (line_nw.find('imau_filename_prev=') != -1):
                out = re.sub(pattern, '{}.nc'.format(year-1), line) 
            elif (line_nw.find('imau_filename_next=') != -1):
                out = re.sub(pattern, '{}.nc'.format(year+1), line) 
            else:
                out = line
            replaced_content += out

    with open(fname, "w") as f:
        f.write(replaced_content)
        
        
