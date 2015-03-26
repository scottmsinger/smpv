#!/usr/bin/env python
#
#    smpv
#

import os
import sys
import re
import shutil
import stat
import string
import inspect
import filecmp
import datetime
import ConfigParser
from optparse import OptionParser

import tip.studio.publish.pm

#
# smpv_file
#
# a class for 
#
class smpv_file():
    
    s_src_file = ""
    s_ini_file = ""
    s_smpv_dir = "./.smpv"
    
    dct_stat_key = {"no_dir" : 0,
                    "not_added" : 1,
                    "checked_in" : 2,
                    "checked_out" : 3 }

    dct_mssg_key = {"info" : 1,
                    "warning" : 2,
                    "error" : 3,
                    "pass" : 0 }
    
    i_info_print = 0
    
    cfgp_ini = ConfigParser.SafeConfigParser();
    
    def __init__(self):
        self.s_ini_file = "./.smpv/smpv.ini"
    
    #tip.studio.publish.pm.makedirs(options.s_dest_dir)        
    def smpv_add(self, s_file_name):
        # if they don't exist already:
        #     create .smpv directory and .smpv/smpv.ini file
        self.s_src_file = s_file_name

        self.smpv_messages("info", "inside svmp_add")
        i_stat = self.smpv_stat(s_file_name)
        
        if(i_stat == self.dct_stat_key["no_dir"]):
            i_stat = self.smpv_env_create(s_file_name)
            i_stat = self.smpv_stat(s_file_name)
        
        if(i_stat == self.dct_stat_key["not_added"]):
            # copy the file to ./.smpv/filename.ext.0000_smpv
            self.smpv_messages("info", "add() adding new section for"+self.s_src_file)
            fp_smpv = file(self.s_ini_file, "r+")
            s_file_sec = self.s_src_file
            s_version_sec = s_file_sec+".0000_smpv"
            self.cfgp_ini.add_section(s_file_sec)
            self.cfgp_ini.set(s_file_sec, "latest_vers", "0")
            self.cfgp_ini.set(s_file_sec, "latest_rev", "0")
            self.cfgp_ini.set(s_file_sec, "version_0", s_version_sec)
            self.cfgp_ini.set(s_file_sec, "status", "checked_in")
            self.cfgp_ini.set(s_file_sec, "latest_user", "you")

            dt_now = datetime.datetime.now()
            s_date_time = dt_now.strftime("%Y-%m-%d %H:%M")

            self.cfgp_ini.add_section(s_version_sec)
            self.cfgp_ini.set(s_version_sec, "file", s_version_sec)
            self.cfgp_ini.set(s_version_sec, "version", "0")
            self.cfgp_ini.set(s_version_sec, "revision", "0")
            self.cfgp_ini.set(s_version_sec, "date_time", s_date_time)
            self.cfgp_ini.set(s_version_sec, "notes", "Initial add from disk")
                       
            # add to [smpv]
            sa_smpv = self.cfgp_ini.items("smpv")
            i_idx = sa_smpv.__len__()
            s_item = "file_"+str(i_idx)
            self.cfgp_ini.set("smpv", s_item, self.s_src_file)
            self.cfgp_ini.write(fp_smpv)
            fp_smpv.close()
            
            s_out_file_name = self.s_smpv_dir+"/"+s_version_sec
            shutil.copy (s_file_name, s_out_file_name)
            #os.chmod(s_file_name, 0444)
            osstat = os.stat(s_file_name)
            oct_perm = oct(osstat.st_mode)
            print oct_perm
            #if(oct_perm[6] != int(4) and oct_perm[6] != int(6)):
            #if(int(oct_perm[6]) % int(1) == 0):
            #if(int(oct_perm) % 1 == 0):
            # if it's executable by user or other at add time - make it executable by all
            if(bool(osstat.st_mode & stat.S_IXOTH) or bool(osstat.st_mode & stat.S_IXUSR)):
                os.chmod(s_file_name, 0555)
            else:
                os.chmod(s_file_name, 0444)
            return(0)
        if(i_stat == self.dct_stat_key["checked_out"] or i_stat == self.dct_stat_key["checked_in"] ):
            self.smpv_messages("error", "_add file already added "+s_file_name)
            return(-1)
    
    def smpv_checkout(self, s_file_name):
        #check to see if file registered:
        #    if not: return 0 w/ message telling the user to add the file
        #    if so: check status
        #        if locked by user: copy and register, set permissions to RO
        #    if not: error out with mssg telling user file not checked out
        self.smpv_messages("info", "inside svmp_checkout")
        i_stat = self.smpv_stat(s_file_name)
        self.smpv_messages("info", "i_stat = " + str(i_stat))
        if(i_stat == self.dct_stat_key["no_dir"]):
            self.smpv_messages("error", "checkout - directory: "+s_file_name+" not under smpv please smpv_add it")
            return -1
        elif(i_stat == self.dct_stat_key["not_added"]):
            self.smpv_messages("error", "checkout - file: "+s_file_name+" not under smpv please smpv_add it")
            return -1
        elif(i_stat == self.dct_stat_key["checked_out"]):
            self.smpv_messages("error", "checkout - file: "+s_file_name+" already locked")
            return -1
        else:
            fp_smpv = file(self.s_ini_file, "r+")
            s_file_sec = s_file_name
            s_latest_vers = self.cfgp_ini.get(s_file_sec, "latest_vers")
            s_file = self.cfgp_ini.get(s_file_sec, "version_"+s_latest_vers)
            self.smpv_messages("pass", "checking out: "+s_file_name+" : version "+ s_latest_vers)
            #os.chmod( s_file_name, 0666)
            osstat = os.stat(s_file_name)
            oct_perm = oct(osstat.st_mode)
            if(int(oct_perm) % 1 == 0):
                os.chmod(s_file_name, 0777)
            else:
                os.chmod(s_file_name, 0666)
            
            s_file = self.cfgp_ini.set(s_file_sec, "status", "checked_out")
            self.cfgp_ini.write(fp_smpv)
            fp_smpv.close()
       
    def smpv_checkin(self, s_file_name, s_comment):
        #check to see if file registered:
        #    if not: error out w/ message telling the user to add the file
        #    if so: check status
        #        if checkedin: error out w/ message that file not checked out
        #        if not: change permissions on file to RW
        self.smpv_messages("info", "inside svmp_checkin")
        i_stat = self.smpv_stat(s_file_name)
        if(i_stat == self.dct_stat_key["no_dir"]):
            self.smpv_messages("error", "checkin - file: "+s_file_name+" not under smpv please smpv_add it")
            return -1
        elif(i_stat == self.dct_stat_key["not_added"]):
            self.smpv_messages("error", "checkin - file: "+s_file_name+" not under smpv please smpv_add it")
            return -1
        elif(i_stat == self.dct_stat_key["checked_in"]):
            self.smpv_messages("error", "checkin - file: "+s_file_name+" not locked")
            return -1
        else:
            fp_smpv = file(self.s_ini_file, "r+")
            s_file_sec = s_file_name
            s_latest_vers = self.cfgp_ini.get(s_file_sec, "latest_vers")
            s_file = self.cfgp_ini.get(s_file_sec, "version_"+s_latest_vers)
            s_curr_file_path = self.s_smpv_dir+"/"+s_file
            i_ident = filecmp.cmp(s_file_name, s_curr_file_path)

            if( i_ident == 0):
                
                #if(s_comment.__len__() < 1):
                if(s_comment == None):
                    s_comment = raw_input("Enter comment then return>")
                
                dt_now = datetime.datetime.now()
                s_date_time = dt_now.strftime("%Y-%m-%d %H:%M")
           
                i_latest_vers = int(s_latest_vers);
                i_next_vers = i_latest_vers + 1
                s_next_vers = str(i_next_vers).zfill(4)
                s_out_file_name = s_file_sec+"."+s_next_vers+"_smpv"
                s_out_file_path = self.s_smpv_dir+"/"+s_out_file_name
                shutil.copy (s_file_name, s_out_file_path)
                #need to preserve executable state
                osstat = os.stat(s_file_name)
                oct_perm = oct(osstat.st_mode)
                if(int(oct_perm) % 1 == 0):
                    os.chmod(s_file_name, 0555)
                else:
                    os.chmod(s_file_name, 0444)
            
                s_version_sec = s_out_file_name
                self.smpv_messages("pass", "checking in: "+s_file_name+" : version "+ s_next_vers)
                self.cfgp_ini.set(s_file_sec, "status", "checked_in")
                #self.cfgp_ini.set(s_file_sec, "version", "checked_in")
                self.cfgp_ini.set(s_file_sec, "latest_vers", str(i_next_vers))
                #self.cfgp_ini.set(s_file_sec, "latest_rev", "r.")
                self.cfgp_ini.set(s_file_sec, "version_"+str(i_next_vers), s_version_sec)
                self.cfgp_ini.set(s_file_sec, "status", "checked_in")
                self.cfgp_ini.set(s_file_sec, "latest_user", "you")

                self.cfgp_ini.add_section(s_version_sec)
                self.cfgp_ini.set(s_version_sec, "file", s_version_sec)
                self.cfgp_ini.set(s_version_sec, "version", str(i_next_vers))
                self.cfgp_ini.set(s_version_sec, "revision", "0")
                self.cfgp_ini.set(s_version_sec, "date_time", s_date_time)
                self.cfgp_ini.set(s_version_sec, "notes", s_comment)
                self.cfgp_ini.write(fp_smpv)
            else:
                self.smpv_messages("warning", "_checkin: no changes to file: "+s_file_name+"; reverting file")
                shutil.copy (s_curr_file_path, s_file_name)
                osstat = os.stat(s_file_name)
                oct_perm = oct(osstat.st_mode)
                if(int(oct_perm) % 1 == 0):
                    os.chmod(s_file_name, 0555)
                else:
                    os.chmod(s_file_name, 0444)
                self.cfgp_ini.set(s_file_sec, "status", "checked_in")
                self.cfgp_ini.write(fp_smpv)
                
            fp_smpv.close()
            return(0)
         
    def smpv_history(self, s_file_name):
        self.smpv_messages("info", "inside svmp_history")
        i_stat = self.smpv_stat(s_file_name)
        if(i_stat == self.dct_stat_key["no_dir"]):
            self.smpv_messages("error", "checkout - file: "+s_file_name+" not under smpv please smpv_add it")
            return -1
        elif(i_stat == self.dct_stat_key["not_added"]):
            self.smpv_messages("error", "checkout - file: "+s_file_name+" not under smpv please smpv_add it")
            return -1
        else:
            fp_smpv = file(self.s_ini_file, "r")
            s_file_sec = s_file_name
            s_status = self.cfgp_ini.get(s_file_sec, "status")
            s_latest_vers = self.cfgp_ini.get(s_file_sec, "latest_vers")
            i_latest_vers = int(s_latest_vers)
            s_latest_rev = self.cfgp_ini.get(s_file_sec, "latest_rev")
            
            print "\nsmpv_history for: "+s_file_name
            print "file:"
            print "    status          "+s_status
            print "    latest_version  "+s_latest_vers
            print "    latest_revision "+s_latest_rev
            i_vers = 0
            print "\nversions:"
            while (i_vers <= i_latest_vers):
                s_curr_vers = "version_"+str(i_vers)
                s_version_sec = self.cfgp_ini.get(s_file_sec, s_curr_vers)
                s_date_time = self.cfgp_ini.get(s_version_sec, "date_time")
                s_revision = self.cfgp_ini.get(s_version_sec, "revision")
                if(int(s_revision) == 0):
                    s_revision = "-"
                s_comment = self.cfgp_ini.get(s_version_sec, "notes")
                print "    version: "+str(i_vers)
                print "    revision: r"+s_revision
                print "    date_time:   "+s_date_time
                print "    notes:   "+s_comment
                print ""
                i_vers += 1
            fp_smpv.close()            
            return(0)
       
    def smpv_status(self, s_file_name):
        self.smpv_messages("info", "inside svmp_status")
        i_stat = self.smpv_stat(s_file_name)
        if(i_stat == self.dct_stat_key["no_dir"]):
            self.smpv_messages("error", "status - file: "+s_file_name+" not under smpv please smpv_add it")
            return -1
        elif(i_stat == self.dct_stat_key["not_added"]):
            self.smpv_messages("error", "status - file: "+s_file_name+" not under smpv please smpv_add it")
            return -1
        else:
            fp_smpv = file(self.s_ini_file, "r")
            s_file_sec = s_file_name
            s_status = self.cfgp_ini.get(s_file_sec, "status")
            s_latest_vers = self.cfgp_ini.get(s_file_sec, "latest_vers")
            i_latest_vers = int(s_latest_vers)
            s_latest_rev = self.cfgp_ini.get(s_file_sec, "latest_rev")
            
            print "\nsmpv_history for: "+s_file_name
            print "    status          "+s_status
            print "    latest_version  "+s_latest_vers
            print "    latest_revision "+s_latest_rev
            i_latest_vers = int(s_latest_vers)
            s_curr_vers = "version_"+str(i_latest_vers)
            s_version_sec = self.cfgp_ini.get(s_file_sec, s_curr_vers)
            s_date_time = self.cfgp_ini.get(s_version_sec, "date_time")
            print "    date_time:   "+s_date_time
            fp_smpv.close()            
            return(0)
       
    def smpv_revert(self, s_file_name):
        self.smpv_messages("info", "inside svmp_revert")
        i_stat = self.smpv_stat(s_file_name)
        if(i_stat == self.dct_stat_key["no_dir"]):
            self.smpv_messages("error", "revert - file: "+s_file_name+" not under smpv please smpv_add it")
            return -1
        elif(i_stat == self.dct_stat_key["not_added"]):
            self.smpv_messages("error", "revert - file: "+s_file_name+" not under smpv please smpv_add it")
            return -1
        elif(i_stat == self.dct_stat_key["checked_in"]):
            self.smpv_messages("error", "revert - file: "+s_file_name+" not locked")
            return -1
        else:
            fp_smpv = file(self.s_ini_file, "r+")
            s_file_sec = s_file_name
            s_latest_vers = self.cfgp_ini.get(s_file_sec, "latest_vers")
            s_file = self.cfgp_ini.get(s_file_sec, "version_"+s_latest_vers)
            s_curr_file_path = self.s_smpv_dir+"/"+s_file
            shutil.copy (s_curr_file_path, s_file_name)
            #need to preserve executable state
            osstat = os.stat(s_file_name)
            oct_perm = oct(osstat.st_mode)
            if(oct_perm[6] != int(4) and oct_perm[6] != int(6)):
                os.chmod(s_file_name, 0445)
            else:
                os.chmod(s_file_name, 0444)
            self.cfgp_ini.set(s_file_sec, "status", "checked_in")
            self.cfgp_ini.write(fp_smpv)
            fp_smpv.close()            
            return(0)
            

    def smpv_recall(self, s_file_name, s_new_file_name, i_vers):
        self.smpv_messages("info", "inside svmp_recall")
        i_stat = self.smpv_stat(s_file_name)
        if(i_stat == self.dct_stat_key["no_dir"]):
            self.smpv_messages("error", "recall - file: "+s_file_name+" not under smpv please smpv_add it")
            return -1
        elif(i_stat == self.dct_stat_key["not_added"]):
            self.smpv_messages("error", "recall - file: "+s_file_name+" not under smpv please smpv_add it")
            return -1
        elif(i_stat == self.dct_stat_key["checked_out"]):
            self.smpv_messages("error", "recall - file: "+s_file_name+" checkedout ")
            return -1
        else:
            fp_smpv = file(self.s_ini_file, "r")
            s_file_sec = s_file_name
            s_latest_vers = self.cfgp_ini.get(s_file_sec, "latest_vers")
            if(int(s_latest_vers) < i_vers):
                self.smpv_messages("error", "recall requested version for: "+s_file_name+" is greater than latest version "+s_latest_vers)
                fp_smpv.close()
                return(-1)
            s_file = self.cfgp_ini.get(s_file_sec, "version_"+str(i_vers))
            s_recall_file_path = self.s_smpv_dir+"/"+s_file
            shutil.copy (s_recall_file_path, s_new_file_name)
            #need to preserve executable state
            osstat = os.stat(s_file_name)
            oct_perm = oct(osstat.st_mode)
            if(int(oct_perm) % 1 == 0):
                os.chmod(s_file_name, 0777)
            else:
                os.chmod(s_file_name, 0666)
            fp_smpv.close()            
            return(0)
    
    def smpv_revup(self, s_file_name, i_version, i_revision):
        self.smpv_messages("info", "inside svmp_revup")
        i_stat = self.smpv_stat(s_file_name)
        if(i_stat == self.dct_stat_key["no_dir"]):
            self.smpv_messages("error", "revup - file: "+s_file_name+" not under smpv please smpv_add it")
            return -1
        elif(i_stat == self.dct_stat_key["not_added"]):
            self.smpv_messages("error", "revup - file: "+s_file_name+" not under smpv please smpv_add it")
            return -1
        elif(i_stat == self.dct_stat_key["checked_out"]):
            self.smpv_messages("error", "revup - file: "+s_file_name+" already locked; needs to be checkedin")
            return -1
        else:
            fp_smpv = file(self.s_ini_file, "r+")
            s_file_sec = s_file_name
            s_latest_rev = self.cfgp_ini.get(s_file_sec, "latest_rev")
            i_latest_rev = int(s_latest_rev)
            if(i_revision <= i_latest_rev):
                self.smpv_messages("error", "revup - requested revision is less than : "+s_file_name+" latest revision of r" + s_latest_rev)
                fp_smpv.close()            
                return(-1)
            s_latest_vers = self.cfgp_ini.get(s_file_sec, "latest_vers")
            i_latest_vers = int(s_latest_vers)
            if(i_version > i_latest_vers):
                self.smpv_messages("error", "revup - requested version is greater than : "+s_file_name+" latest version of " + s_latest_vers)
                fp_smpv.close()            
                return(-1)
            s_vers_sec = self.cfgp_ini.get(s_file_sec, "version_"+str(i_version))
            self.cfgp_ini.set(s_vers_sec, "revision", str(i_revision))
            self.cfgp_ini.set(s_file_sec, "latest_rev", str(i_revision))
            self.cfgp_ini.write(fp_smpv)
            fp_smpv.close()            
            return(0)
            
            
            
    
    def smpv_env_create(self, s_file_name):
        self.smpv_messages("info", "inside svmp_env_create")
        # create the ./.smpv directory
        try:
            os.mkdir(self.s_smpv_dir)
            #tip.studio.publish.pm.makedirs(self.s_smpv_dir)
        except:
            return 1
        # create the ./.smpv/smpv.ini file
        fp_smpv = file(self.s_ini_file, mode="w")
        self.cfgp_ini.add_section("smpv")
        self.cfgp_ini.write(fp_smpv)
        fp_smpv.close()
        return 0
        
    def smpv_ini_dir(self):
        self.smpv_messages("info", "inside svmp_ini_dir")
    
    def smpv_list_vers(self):
        self.smpv_messages("info", "inside svmp_list_vers")
        
    def smpv_stat(self, s_file_name):
        self.smpv_messages("info", "inside svmp_stat")
        # base on file/dir status return the following:
        i_stat = os.path.exists(self.s_smpv_dir)
        #    no dir = 0
        if(i_stat == 0):
            self.smpv_messages("warning", "location: "+ s_file_name +" doesn't exist")
            return i_stat
        
        fp_smpv = file(self.s_ini_file, mode="r")
        ## need to move this - it's in the wrong place and it all works only
        ## through the grace of god.
        self.cfgp_ini.readfp( fp_smpv, self.s_ini_file)
        # open up the ./.smpv/smpv.ini file to check status
        #    not_added = 1
        if(self.cfgp_ini.has_section(s_file_name) != 1):
            fp_smpv.close()
            return(self.dct_stat_key["not_added"])
        #print s_file_name
        s_stat = self.cfgp_ini.get(s_file_name, "status")
        return self.dct_stat_key[s_stat]

        fp_smpv.close()
        return 2
    
    def smpv_messages(self, s_message_code, s_message):
        s_base = "smpv_"
        i_print = 0
        i_message_level = self.dct_mssg_key[s_message_code]
        if(i_message_level == 0):
            s_message_level = ""
            i_print = 1
        elif(i_message_level == 1 and self.i_info_print > 0):
            s_message_level = "INFO"
            i_print = 1
        elif(i_message_level == 2):
            s_message_level = "WARNING"
            i_print = 1
        elif(i_message_level == 3):
            s_message_level = "ERROR"
            i_print = 1
        if(i_print):
            print(s_message_level+"::"+s_base+":"+s_message)
        

def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("--add", action="store_true", dest="b_add", default=False)
    parser.add_option("--checkin",action="store_true", dest="b_checkin", default=False)
    parser.add_option("--checkout",action="store_true", dest="b_checkout", default=False)
    parser.add_option("--revert",action="store_true", dest="b_revert", default=False)
    #parser.add_option("--recall",action="store_true", dest="b_recall", default=False)
    parser.add_option("--recall_vers",action="store", type="int", dest="i_recall_vers")
    parser.add_option("--recall_file", action="store", type="string", dest="s_recall_file_name")
    #parser.add_option("--revup",action="store_true", dest="b_revup", default=False)
    parser.add_option("--revup_vers", action="store", type="int", dest="i_revup_vers")
    parser.add_option("--revup_rev", action="store", type="int", dest="i_revup_rev")
    parser.add_option("--history",action="store_true", dest="b_history", default=False)
    parser.add_option("--status",action="store_true", dest="b_status", default=False)
    parser.add_option("--file", action="store", type="string", dest="s_file_name")
    parser.add_option("--comment", action="store", type="string", dest="s_comment")

    (options, args) = parser.parse_args()
    
    smpv_curr = smpv_file();
    
    if( options.b_add and options.s_file_name != None):
        smpv_curr.smpv_add(options.s_file_name)
    elif( options.b_checkin  and options.s_file_name != None):
        smpv_curr.smpv_checkin(options.s_file_name, options.s_comment)
    elif( options.b_checkout  and options.s_file_name != None):
        smpv_curr.smpv_checkout(options.s_file_name)
    elif( options.b_revert  and options.s_file_name != None):
        smpv_curr.smpv_revert(options.s_file_name)
    elif( options.b_history  and options.s_file_name != None):
        smpv_curr.smpv_history(options.s_file_name)
    elif( options.b_status  and options.s_file_name != None):
        smpv_curr.smpv_status(options.s_file_name)
    elif( options.i_recall_vers != None and options.s_recall_file_name != None ):
        smpv_curr.smpv_recall(options.s_file_name, options.s_recall_file_name, options.i_recall_vers)
    elif( options.i_revup_vers != None  and options.i_revup_rev != None):
        print(options.i_revup_vers)
        print(options.i_revup_rev)
        smpv_curr.smpv_revup(options.s_file_name, options.i_revup_vers, options.i_revup_rev)
        

if __name__ == "__main__":
    main()

