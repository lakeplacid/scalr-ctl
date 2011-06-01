'''
Created on Feb 21th, 2011

@author: Dmytro Korsakov
'''

import sys
import inspect
import logging
from optparse import OptionParser

import commands
from config import Configuration, ScalrCfgError, ScalrEnvError


def split_options(args):
	'''
	@return ([options], subcommand, [args])
	'''
	for arg in args[1:]:
		index = args.index(arg)
		prev = args[args.index(arg)-1]		
		if not arg.startswith('-') and (prev.startswith('--') or not prev.startswith('-') or index == 1):
			return (args[1:index], arg, args[index+1:])			
	return (args[1:], None, [])

def get_commands():
	hs = []
	for name, obj in inspect.getmembers(commands):
		if inspect.isclass(obj) and hasattr(obj, 'name') and getattr(obj, 'name'):
			hs.append(obj)
	return hs

def main():
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.DEBUG)
	handler = logging.StreamHandler()
	handler.setLevel(logging.DEBUG)
	fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
	handler.setFormatter(fmt)
	logger.addHandler(handler)
	
	subcommands = '\nAvailable subcommands:\n\n' + '\n'.join(sorted([command.name for command in get_commands()]))
	usage='Usage: %s [options] subcommand [args]' % commands.progname
	
	parser = OptionParser(usage=usage, add_help_option=False)
	parser.add_option("--debug", dest="debug", action="store_true", help="Enable debug output")
	parser.add_option("-c", "--config-path", dest="base_path", default=None, help="Path to configuration files")
	parser.add_option("-i", "--key-id", dest="key_id", default=None, help="Scalr API key ID")
	parser.add_option("-a", "--access-key", dest="key", default=None, help="Scalr API access key")
	parser.add_option("-u", "--api-url", dest="api_url", default=None, help="Scalr API URL")
	parser.add_option("-h", "--help", dest="help", action="store_true", help="Help")
	
	args, cmd, subargs = split_options(sys.argv)

	options = parser.parse_args(args)[0]
	help = parser.format_help() + subcommands + "\n\nFor more information try '%s help <subcommand>'" % commands.progname
	if not cmd or options.help:
		print help
		sys.exit()

	try:
		c = Configuration(options.base_path)
		c.set_environment(options.key, options.key_id, options.api_url)
		
		if options.debug:
			c.set_logger(logger)
			
	except ScalrEnvError, e:
		if not cmd.startswith('configure') and cmd != 'help':
			print "\nNo login information found."
			print "Please specify options -a -u and -s, or run '%s help configure' to find out how to set login information permanently.\n" % commands.progname
			#print help
			sys.exit()
		
	except ScalrCfgError, e:
		print e 
		sys.exit()

			
	for command in get_commands():
		if cmd == 'help' and len(subargs) == 1 and subargs[0] == command.name:
			print command.usage()
			sys.exit()
			
		if command.name == cmd:
			obj = command(c, *subargs)
			obj.run()
			sys.exit()
	else:
		print help

if __name__ == '__main__':
	main()