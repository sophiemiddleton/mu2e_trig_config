import json
import os

from argparse import ArgumentParser

from codecs import open

def capitalize(word):
    if not word:
        return word
    nLetters=1
    nn = word[0].upper()
    return nn + word[nLetters:]

def generateLogger(args, dictLog, logName, dictStreams):
    name_app = '.fcl'
    if args.evtMode != 'all':
        name_app = '_'+args.evtMode+'.fcl'
    
    loggerFileName       = args.outdir+"/"+logName+name_app
    loggerConfigFileName = args.outdir+"/"+logName+'Config'+name_app
   
    os.system("chmod 755 {}".format(loggerConfigFileName))
    os.system("chmod 755 {}".format(loggerFileName))
    loggerMenu   = open(loggerFileName, 'w') 
    loggerConfig = open(loggerConfigFileName, 'w') 
    
    tagName = capitalize(logName)
    
    loggerConfig.write(tagName+"Config: {\n")
 
    
    list_of_logger_streams = []
    for k in dictLog:
        if dictLog[k]['enabled'] == 0: continue
        vv = k.split("_")
        streamName = vv[0]
        for i in range(1,len(vv)): streamName = streamName + capitalize(vv[i])
        streamName = streamName+"Output"
        list_of_logger_streams.append(streamName)
        #
        loggerConfig.write('   {}:'.format(streamName)+' { \n')
        loggerConfig.write('      module_type: RootDAQOutput \n')
        loggerConfig.write('      SelectEvents : {}\n'.format(json.dumps(dictStreams[k])))
        loggerConfig.write('      maxSubRuns   : 1\n')
        loggerConfig.write('      fileName     : "{}.art\"\n'.format(k))
        loggerConfig.write('   }\n\n')
    loggerConfig.write("}\n")
    loggerConfig.close()
     
    loggerMenu.write(tagName+"Outputs: {\n")
    loggerMenu.write("  outputs: [")
    for i in range(len(list_of_logger_streams)):
        k = list_of_logger_streams[i]
        if i!= len(list_of_logger_streams)-1: 
            loggerMenu.write("{},".format(k))
        else:
            loggerMenu.write("{}".format(k))
    #
    print("[generateLogger] {} OUTPUT PATHS FOUND (): {}".format(logName, len(list_of_logger_streams), list_of_logger_streams))
    loggerMenu.write("]\n")
    loggerMenu.write("}\n")

    loggerMenu.write(tagName+"Menu: {\n")
    loggerMenu.write("  end_paths: [ outputs ] \n")
    loggerMenu.write("}\n")
    loggerMenu.close()

    os.system("chmod 444 {}".format(loggerConfigFileName))
    os.system("chmod 444 {}".format(loggerFileName))

################################################################################
##
##
##
################################################################################
def generateMenu(args,  dictMenu, menuName, dictStreams, proc_name):
    name_app = '.fcl'
    if args.evtMode != 'all':
        name_app = '_'+args.evtMode+'.fcl'
    trigMenuFileName = args.outdir+"/"+menuName+name_app
    psConfigFileName = args.outdir+"/"+menuName+'PSConfig'+name_app
    
    os.system("chmod 755 {}".format(trigMenuFileName))
    os.system("chmod 755 {}".format(psConfigFileName))

    trigMenu = open(trigMenuFileName, 'w')
    psConfig = open(psConfigFileName, 'w')
    
    tag = capitalize(menuName)
    trigMenu.write(tag+": {\n")
    trigMenu.write("  trigger_paths: [\n")
    psConfig.write(tag+"PSConfig: {\n")
  
    list_of_calo_trk_paths = []
    for k in dictMenu:
        if dictMenu[k]['enabled'] == 0: continue
        evtModes = dictMenu[k]['eventModeConfig']
        evtModeCheck= args.evtMode == "all"
        for ll in range(len(evtModes)):
            if args.evtMode != "all" and args.evtMode == evtModes[ll]["eventMode"]: 
                evtModeCheck = True
                break
        if evtModeCheck: 
            list_of_calo_trk_paths.append(k)

    for i in range(len(list_of_calo_trk_paths)):
        path = list_of_calo_trk_paths[i]
        if i!= len(list_of_calo_trk_paths)-1:
            trigMenu.write('     "{}:{}",\n'.format(dictMenu[path]['bit'], path))
        else:
            trigMenu.write('     "{}:{}"\n'.format(dictMenu[path]['bit'], path))
        #
        vv=path.split("_")
        streamName = vv[0]
        for i in range(1,len(vv)): streamName = streamName + capitalize(vv[i])
        psConfig.write("   {}PS:".format(streamName)+" { \n")
        psConfig.write("      module_type: PrescaleEvent \n")
        evtModes = dictMenu[path]['eventModeConfig']
        psInput = "[ "
        notFirst = False
        for ll in range(len(evtModes)):
            if args.evtMode != "all" and args.evtMode != evtModes[ll]["eventMode"]: continue
            if notFirst: psInput += ","
            psInput += " { eventMode: "+"{}".format(evtModes[ll]["eventMode"])+" prescale:{}".format(evtModes[ll]["prescale"])+"}"
            notFirst = True
        psInput += " ]"
        
        psConfig.write("      eventModeConfig : {}\n".format(psInput))
        psConfig.write("}\n\n")
        
        vv=dictMenu[path]['eventModeConfig']
        for dd in vv:
            for s in dd['streams']:
                if path not in dictStreams[s]:
                    trg_path = proc_name+":"+path
                    dictStreams[s].append(trg_path)
        
    #
    print("[generateMenu] {} TRIGGER PATHS FOUND (): {}".format(menuName, len(list_of_calo_trk_paths), list_of_calo_trk_paths)) 
    #
    psConfig.write("}\n")
    psConfig.close()
    trigMenu.write("  ]\n")
    trigMenu.write("}\n")
    trigMenu.close()
    
    os.system("chmod 444 {}".format(trigMenuFileName))
    os.system("chmod 444 {}".format(psConfigFileName))



#def generate(args):
def generate(raw_args=None):
    #--------------------------------------------------------------------------------
    parser = ArgumentParser()
    parser.add_argument("-mf", "--menu-file",
                        dest="menuFile", default="data/physMenu.json",
                        help="Input Menu file")
    parser.add_argument("-q", "--quiet",
                        action="store_false", dest="verbose", default=True,
                        help="don't print status messages to stdout")
    parser.add_argument("-o", "--outdir",
                        dest="outdir", default="gen",
                        help="Outout directory")
    parser.add_argument("-evtMode", "--event-mode",dest="evtMode",
                        default="all",
                        help="Specify a single event mode if you want a single-event-mode Menu: OnSpill, OffSpill. The default is 'all'")

    args = parser.parse_args(raw_args)

    os.system("mkdir -p {}".format(args.outdir))

    #check the event mode
    allowed_evtModes = ['OnSpill', 'OffSpill', 'all']
    if args.evtMode not in allowed_evtModes:
        print("[generateMenuFromJSON] EVENT-MODE {} NOT ALLOWED! THE POSSIBLE OPTIONS ARE: {}".format(args.evtMode, allowed_evtModes))
        exit(1)
   
    #--------------------------------------------------------------------------------
    tag = args.menuFile.split('/')[-1].split('.')[0]

    with open(args.menuFile) as f:
        conf = json.load(f)
        keys = conf.keys()
        print("[generateMenuJSON] KEYS FOUND: {}".format(keys))
        data_streams = {}
        for k in conf['dataLogger_streams']:
            data_streams[k] = []

        dict_trkcal_triggers = conf['trigger_paths']
        trkcal_proc_name     = conf['trkcal_filter_process_name']
        generateMenu(args, dict_trkcal_triggers, 'trig_'+tag, data_streams, trkcal_proc_name)
        print("[generateMenuJSON] DATA STREAMS FOUND: {}".format(data_streams))        

        dict_agg_triggers = conf['agg_trigger_paths']
        add_proc_name     = conf['crv_agg_process_name']
        generateMenu(args, dict_agg_triggers, 'agg_'+tag, data_streams, add_proc_name)

        #now produce the logger menus
        dict_logger = conf['dataLogger_streams']
        generateLogger(args, dict_logger, 'trigLogger_'+tag, data_streams)        
        #
        dict_logger = conf['lumiLogger_streams']
        lumi_streams =  {}
        lumi_streams['lumi'] = []
        generateLogger(args, dict_logger, 'trigLumiLogger_'+tag, lumi_streams)
        
   
    # psConfig.write("}\n")
    # psConfig.close()
    # trigMenu.write("  ]\n")
    # trigMenu.write("}\n")
    # trigMenu.close()
    
    # os.system("chmod 444 {}".format(trigMenuFileName))
    # os.system("chmod 444 {}".format(psConfigFileName))


if __name__ == "__main__":
    # parser = ArgumentParser()
    # parser.add_argument("-mf", "--menu-file",
    #                     dest="menuFile", default="data/physMenu.json",
    #                     help="Input Menu file")
    # parser.add_argument("-q", "--quiet",
    #                     action="store_false", dest="verbose", default=True,
    #                     help="don't print status messages to stdout")
    # parser.add_argument("-o", "--outdir",
    #                     dest="outdir", default="gen",
    #                     help="Outout directory")
    # parser.add_argument("-evtMode", "--event-mode",dest="evtMode",
    #                     default="all",
    #                     help="Specify a single event mode if you want a single-event-mode Menu: OnSpill, OffSpill. The default is 'all'")

    # args = parser.parse_args()
    
    # os.system("mkdir -p {}".format(args.outdir))
    
    #check the event mode
    # allowed_evtModes = ['OnSpill', 'OffSpill', 'all']
    # if args.evtMode not in allowed_evtModes:
    #     print("[generateMenuFromJSON] EVENT-MODE {} NOT ALLOWED! THE POSSIBLE OPTIONS ARE: {}".format(args.evtMode, allowed_evtModes))
    #     exit(1)
        
    #generate(args)
    generate()
