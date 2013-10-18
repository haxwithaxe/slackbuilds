#
# Makefile for Linux version of Dire Wolf.
#

program_name = direwolf

prefix = /usr/local/
ifneq ($(origin PREFIX), undefined)
prefix = $(PREFIX)
endif

datarootdir = $(prefix)share/
docdir = $(datarootdir)doc/$(program_name)/
datadir = $(datarootdir)$(program_name)/
exec_prefix = $(prefix)
bindir = $(exec_prefix)bin/
srcdir = $(dir $(lastword $(MAKEFILE_LIST)))

INSTALL_PROGRAM = install --mode=755 -t
INSTALL_DATA = install --mode=644 -t
ARCH_CMD = tar zcvf
MKDIR = mkdir -p 

TEST_DIR = $(srcdir)tests/
SRC_ARCH = direwolf-src.tar.gz
ARCH_CMD = tar zcvf

SRCS = direwolf.c fsk_gen_filter.o fsk_demod.c hdlc_rec.c fcs_calc.c ax25_pad.c decode_aprs.c \
	server.c kiss.c kissnet.c kiss_frame.c hdlc_send.c fcs_calc.c gen_tone.c audio.c \
	digipeater.c dedupe.c tq.c xmit.c beacon.c

BINS = direwolf decode_aprs text2tt tt2text ll2utm utm2ll
SRC_CODE = *.c *.h regex/* misc/* utm/*
DOCS = tocalls.txt CHANGES.txt LICENSE* User-Guide.pdf

MAKEFILE = Makefile
CONFIGS = direwolf.conf
ICON = dw-icon.png dw-icon.rc dw-icon.ico
XDG_RES = direwolf.desktop
START_SCRIPTS = dw-start.sh

ifdef $(RASPI)
	START_SCRIPTS += rpi-audio.sh
	DOCS += Raspberry-Pi-APRS.pdf
endif

ifdef $(WINDOWS)
	DOCS += Quick-Start-Guide-Windows.pdf
endif

all : direwolf decode_aprs text2tt tt2text ll2utm utm2ll


#
# On Linux, you have a choice of using either OSS or ALSA
# sound systems depending on what is supported on your platform.
# ALSA is newer and the the default as shown below.
# Remove "-DUSE_ALSA" if you prefer to use OSS.
#

SOUND_SYSTEM ?= USE_ALSA
CFLAGS = -D$(SOUND_SYSTEM) -O3 -pthread

# Main application.

direwolf : direwolf.o config.o fsk_gen_filter.o fsk_demod.o hdlc_rec.o \
		hdlc_rec2.o redecode.o rdq.o rrbb.o \
		fcs_calc.o ax25_pad.o \
		decode_aprs.o server.o kiss.o kissnet.o kiss_frame.o hdlc_send.o fcs_calc.o \
		gen_tone.o audio.o digipeater.o dedupe.o tq.o xmit.o \
		ptt.o beacon.o textcolor.o \
		dtmf.o aprs_tt.o tt_user.o tt_text.o igate.o \
		utm.a
	$(CC) -o $@ $^ -lpthread -lrt -lasound -lm

# Optimization for slow processors.

fsk_demod.c : fsk_fast_filter.h

fsk_fast_filter.h : fsk_gen_filter.c
	$(CC) $(CFLAGS) -o gen_fff -DGEN_FFF fsk_gen_filter.c textcolor.c -lm
	$(srcdir)gen_fff > fsk_fast_filter.h

utm.a : LatLong-UTMconversion.o
	$(AR) -cr $@ $^

LatLong-UTMconversion.o : utm/LatLong-UTMconversion.c
	$(CC) $(CFLAGS) -c -o $@ $^

# Optional install step. 
# TODO: Review file locations.

install : direwolf decode_aprs tocalls.txt dw-icon.png direwolf.desktop
	$(MKDIR) $(DESTDIR)$(bindir) $(DESTDIR)$(datadir) $(DESTDIR)$(datarootdir)applications $(DESTDIR)$(datadir)config $(DESTDIR)$(docdir)
	$(INSTALL_PROGRAM) $(DESTDIR)$(bindir) $(BINS)
	$(INSTALL_DATA) $(DESTDIR)$(datadir) $(ICON)
	$(INSTALL_DATA) $(DESTDIR)$(datarootdir)applications $(XDG_RES)
	$(INSTALL_DATA) $(DESTDIR)$(datadir)config dw-start.sh $(CONFIGS)
	$(INSTALL_DATA) $(DESTDIR)$(docdir) $(DOCS)

# Separate application to decode raw data.

decode_aprs : decode_aprs.c ax25_pad.c textcolor.c fcs_calc.c
	$(CC) $(CFLAGS) -o decode_aprs -DTEST $^ -lm

# Convert between text and touch tone representation.

text2tt : tt_text.c
	$(CC) -DENC_MAIN -o text2tt tt_text.c

tt2text : tt_text.c
	$(CC) -DDEC_MAIN -o tt2text tt_text.c

# Convert between Latitude/Longitude and UTM coordinates.

ll2utm : ll2utm.c utm.a
	$(CC) -I utm -o $@ $^ -lm

utm2ll : utm2ll.c utm.a
	$(CC) -I utm -o $@ $^ -lm

##### TESTS

# Test application to generate sound.

tests:
	$(MKDIR) $(TESTDIR)

gen_packets : gen_packets.o  ax25_pad.o hdlc_send.o fcs_calc.o gen_tone.o \
		audio.o tests
	$(CC) $(CFLAGS) -o $(TEST_DIR)$@ $^

testagc : atest.c fsk_demod.c hdlc_rec.c hdlc_rec2.o rrbb.o fcs_calc.c ax25_pad.c decode_aprs.c fsk_demod_agc.h textcolor.c
	$(CC) $(CFLAGS) -o $(TEST_DIR)$@ $^
	$(TEST_DIR)$@ 02_Track_2.wav | grep "packets decoded in" > $@.out

# Unit test for AFSK demodulator

atest : atest.c fsk_gen_filter.c fsk_demod.c hdlc_rec.c hdlc_rec2.o rrbb.o fcs_calc.c ax25_pad.c decode_aprs.c textcolor.c
	$(CC) $(CFLAGS) -o $(TEST_DIR)$@ $^
	$(TEST_DIR)$@ 02_Track_2.wav 

# Unit test for inner digipeater algorithm

dtest : digipeater.c ax25_pad.c dedupe.c fcs_calc.c tq.c textcolor.c
	$(CC) $(CFLAGS) -DTEST -o $(TEST_DIR)$@ $^
	$(TEST_DIR)$@

# Unit test for IGate

itest : igate.c textcolor.c ax25_pad.c fcs_calc.c 
	$(CC) $(CFLAGS) -DITEST -o $(TEST_DIR)$@ $^
	$(TEST_DIR)$@

#### END TESTS

depend : $(SRCS)
	makedepend $(INCLUDES) $^

clean :
	@echo $(srcdir)
	rm -f $(BINS) fsk_fast_filter.h *.o $(TEST_DIR)*

# Package up source code for distribution.

dist-src : $(DOCS) $(CONFIGS) $(ICON) $(START_SCRIPTS)
	cp $(MAKEFILE) $(MAKEFILE).linux
	rm -f ../$(SRC_ARCH)
	($(ARCH_CMD) ../$(SRC_ARCH) \
		$(DOCS) \
		$(CONFIGS) \
		$(MAKEFILE) \
		$(SRC_CODE) \
		$(ICON) \
		$(XDG_RES) \
		$(START_SCRIPTS) )

