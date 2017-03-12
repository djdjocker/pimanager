# -*- coding: utf-8 -*-

import ConfigParser
import logging
import os

LOG_NOTSET = 'notset'
LOG_DEBUG = 'debug'
LOG_INFO = 'info'
LOG_ACCESS = 'access'
LOG_WARNING = 'warn'
LOG_ERROR = 'error'
LOG_CRITICAL = 'critical'

class Config(object):
    options = {}
    casts = {}
    misc = {}
    
    
    _LOGLEVELS = dict([
        (globals().get('LOG_%s' % x), getattr(logging, x)) 
        for x in ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET')
    ])

    def __init__(self):
        """Constructor.
        """
        self.rcfile = os.path.abspath('~/.pimanager.cfg')
        self.rc_exists = False
        if os.path.isfile(self.rcfile):
            selected.rc_exists = True
            self.load()
        
    def __setitem__(self, key, value):
        self.options[key] = value

    def __getitem__(self, key):
        return self.options[key]

    def __getattr__(self, attr):
        if attr in self.options:
            return self.options[attr]
        raise AttributeError
    
    def __setattr__(self, name, value):
        if name in self.options:
            self.options[name] = value
            return True
        return super(Config, self).__setattr__(name, value)
    
    def load(self):
        p = ConfigParser.ConfigParser()
        try:
            p.read([self.rcfile])
            for group in self.parser.option_groups:
                try:
                    for (name,value) in p.items(group.title, raw=True):
                        if value=='True' or value=='true':
                            value = True
                        if value=='False' or value=='false':
                            value = False
                        if value=='None' or value =='none':
                            value = None
                        self.options[name] = value
                except ConfigParser.NoSectionError:
                    pass
                
            #parse the other sections, as well
            for sec in p.sections():
                if sec in map(lambda g: g.title, self.parser.option_groups):
                    continue
                if not self.misc.has_key(sec):
                    self.misc[sec]= {}
                for (name, value) in p.items(sec):
                    if value=='True' or value=='true':
                        value = True
                    if value=='False' or value=='false':
                        value = False
                    self.misc[sec][name] = value
        except IOError:
            pass

    def save(self):
        p = ConfigParser.ConfigParser()
        loglevelnames = dict(zip(self._LOGLEVELS.values(), self._LOGLEVELS.keys()))
        for group in self.parser.option_groups:
            if group.title == 'common':
                continue
            p.add_section(group.title)
            for opt in group.option_list:
                if opt.dest in ('version', 'language', 'translate_out', 'translate_in', 'overwrite_existing_translations', 'install', 'update'):
                    continue
                if opt.dest in self.blacklist_for_save:
                    continue
                if opt.dest in ('loglevel',):
                    p.set(group.title, opt.dest, loglevelnames.get(self.options[opt.dest], self.options[opt.dest]))
        #        elif opt.dest == 'log_handler':
        #            p.set(group.title, opt.dest, ','.join(_deduplicate_loggers(self.options[opt.dest])))
                else:
                    p.set(group.title, opt.dest, self.options[opt.dest])

        for sec in sorted(self.misc.keys()):
            p.add_section(sec)
            for opt in sorted(self.misc[sec].keys()):
                p.set(sec,opt,self.misc[sec][opt])

        # try to create the directories and write the file
        try:
            rc_exists = os.path.exists(self.rcfile)
            if not rc_exists and not os.path.exists(os.path.dirname(self.rcfile)):
                os.makedirs(os.path.dirname(self.rcfile))
            try:
                p.write(file(self.rcfile, 'w'))
                if not rc_exists:
                    os.chmod(self.rcfile, 0600)
            except IOError:
                sys.stderr.write("ERROR: couldn't write the config file\n")
            except Exception, e:
                sys.stderr.write("ERROR : e")

        except OSError:
            # what to do if impossible?
            sys.stderr.write("ERROR: couldn't create the config directory\n")

    def keys(self):
        return self.options.keys()
    
    def items(self):
        return self.options.items()

config = Config()