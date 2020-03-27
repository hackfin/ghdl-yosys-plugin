FROM debian:buster-slim

RUN apt-get update --allow-releaseinfo-change ; \
	apt-get install -y make python wget gnupg

RUN wget -qO - https://section5.ch/section5-apt.key | apt-key add - 

RUN echo "deb http://section5.ch/debian buster non-free" > /etc/apt/sources.list.d/section5.list

RUN apt-get update --allow-releaseinfo-change ; \
	apt-get install -y ghdl iverilog

# RUN apt-get install -y git g++-8 tcl-dev libreadline-dev libffi-dev 

