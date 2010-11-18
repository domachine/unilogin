#!/usr/bin/perl -w
# Author: Dominik Burgdoerfer <dominik.burgdoerfer@uni-ulm.de>
# Script to login automatically to the wireless lan of the university of ulm.
#
# Changelog:
#     Version 0.1.0
#       - pretty quick and dirty.
#       - needs to do logging of potential errors.

use strict;
use Getopt::Long;
use File::Temp qw(tempfile);

# Function prototypes.
sub retrieve_login_data;
sub login;
sub logout;

my %error_table = (0 => "Success",
		   1 => "Failed to connect",
		   2 => "Already logged in");
my $errcode = 0;
my $user = "";
my $pass = "";
my ($fd, $logfile) = tempfile();

close($fd);

my $result = GetOptions("user=s" => \$user,
			"password=s" => \$pass);

if(!$result) {
    exit(1);
}

if(@ARGV == 1) {
    if($ARGV[0] eq "logout") {
	if(logout()) {
	    print "Logout ok\n";
	    exit(0);
	}
	else {
	    print "Logout failed\n";
	    exit(1);
	}
    }
    elsif($ARGV[0] ne "login") {
	print "Invalid extra argument: ".$ARGV[0];
	exit(1);
    }
}

print "Retrieving login data ...";
my $data = retrieve_login_data;

if(@$data) {
    print "done!\n";
}
else {
    print "failed: ".$error_table{$errcode}."\n";
    if($errcode == 1) {
	show_logfile();
    }

    exit(1);
}

my $url = $data->[0];

# Add username and password to the data.
my $post_data = "user=$user&pass=$pass".$data->[1];
my $login_data = [$url, $post_data];

print "Logging in ...";

# Login using the patched data.
if(login($login_data)) {
    print "done!\n";
}
else {
    print "failed: ".$error_table{$errcode}."\n";
    if($errcode == 1) {
	show_logfile();
    }

    exit(1);
}

sub retrieve_login_data {
    my $post_data = "";
    my $url = "";
    my $num_of_lines = 0;

    open(INPUT, "wget uni-ulm.de -O - 2>$logfile |");

    for (<INPUT>)
    {
	if(/.*type=\"hidden\" *name=\"([^\"]+)\" *value=\"([^\"]*)\".*/) {
	    $post_data .= "&$1=$2";
	}
	elsif(/.*form *method="post" *action="([^"]+)".*/) {
	    $url = $1;
	}
	elsif(/[ \t]*<\/ *form *>[ \t]*/) {
	    last;
	}

	++$num_of_lines;
    }

    close(INPUT);

    if($url && $post_data) {
	[$url, $post_data];
    }
    else {
	if($num_of_lines == 0) {
	    $errcode = 1;
	}
	else {
	    $errcode = 2;
	}

	[];
    }
}

sub login {
    my $data = shift;

    open(INPUT, "wget '".$data->[0]."' ".
	 "--post-data='".$data->[1]."' -O - 2>/dev/null |");

    my $logged_in = 1;

    # Search login-form. If it exists, the login failed.
    for (<INPUT>)
    {
	if(/.*form *method="post" *action="([^"]+)".*/) {
	    # Verify form url.
	    if($1 eq $data->[0]) {
		$logged_in = 0;
		last;
	    }
	}
    }

    close(INPUT);

    $logged_in;
}

sub logout {
    open(INPUT, "wget 'http://welcome.uni-ulm.de/logout.html' -O - 2>".
	 $logfile." |");

    my $logged_out = 0;

    for(<INPUT>)
    {
	if(/.*<h1>Logout OK<\/h1>.*/) {
	    $logged_out = 1;
	    last;
	}
    }

    $logged_out;
}

sub show_logfile {
    open(LOG, "<".$logfile);

    for(<LOG>) {
	print $_;
    }

    close(LOG);
    unlink($logfile);
}
