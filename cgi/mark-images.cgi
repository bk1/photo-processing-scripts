#!/usr/bin/perl

use strict;
use Math::BigInt;
use DBI();
use Encode qw(decode encode);
use POSIX qw/strftime/;

use utf8;

use CGI qw(:standard);
charset('utf-8');

my $OUTPUT_DIR = "/var/lib/wwwrun/mark-fotos";
my $log_file = "$OUTPUT_DIR/mark-images.log";

close STDERR;
open STDERR, ">>:utf8", $log_file;

my $git_id     = '$ID$';

my $date = strftime("%F %T", localtime());
my $dir = param("DIR");

print STDERR "$date DIR=$dir\n";

my $indexf = "$dir/indexf.html";
my $datf   = "$OUTPUT_DIR/marked.dat";
my $old_datf = "$OUTPUT_DIR/marked.dat.1";
if (-f $old_datf) {
    unlink($old_datf);
}
if (-f $datf) {
    rename $datf, $old_datf;
}

my $enc_flags = Encode::FB_CROAK | Encode::LEAVE_SRC;

my $count = param("COUNT");
my @names = param();
my $names = join(":", @names);

my $checked = "";
my $texts   = "";
for (my $i = 0; $i < $count; $i++) {
    my $c = param("C$i");
    if ($c) {
        my $file = param("I$i");
        $checked .= "$file\n";
    }
    my $t = param("T$i");
    if ($t) {
        my $file = param("I$i");
        $texts .= "$file\t:\t$t\n";
    }
}

open DAT, ">:utf8", $datf;
print DAT "$date\n\n";
print DAT "CHECKED:\n";
print DAT "$checked\n";
print DAT "TEXTS:\n";
print DAT "$texts\n";
close DAT;

binmode STDOUT, ":utf8";

unless (-r $indexf) {
    print STDERR "$date $indexf not readable\n";
}

unless (-f $indexf) {
    print STDERR "$date $indexf not file\n";
}

print header(-type => 'text/html', -charset => 'utf-8');

open INDEXF, "<:utf8", $indexf;

print STDERR "$date $indexf opened\n";

my $skipping = 0;
while (my $line = <INDEXF>) {
    if ($line =~ m@</body[^<>]*>@) {
        print STDERR "$date $indexf footer reached\n";
        $skipping = 0;
    }
    if ($skipping) {
        next;
    }
    if ($line =~ m@</head[^<>]*>@) {
        print "<base href=\"file://$dir/\">\n";
        print STDERR "$date $indexf base printed\n";
    }
    print $line;
    if ($line =~ m/<body[^<>]*>/) {
        $checked =~ s/\n/<br>\n/g;
        $texts   =~ s/\n/<br>\n/g;
        print "<p>$checked\n";
        print "<p>$texts\n";
        print "<p>DIR=$dir\n";
        print "<p>cd $dir\n";
        print "<p><a href=\"file://$dir/index.html\">index.html</a>\n";
        print "<p><a href=\"file://$dir/indexf.html\">indexf.html</a>\n";
        $skipping = 1;
        print STDERR "$date $indexf body reached\n";
    }
}
close INDEXF;
