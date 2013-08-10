from glue.ligolw import param, ligolw
from glue.ligolw import utils, table, lsctables

from pylal.series import read_psd_xmldoc
from pylal.series import build_COMPLEX16FrequencySeries
from pylal.series import parse_COMPLEX16FrequencySeries
from pylal.series import build_REAL8TimeSeries
from pylal.series import parse_REAL8TimeSeries

def make_fseries_xmldoc(psddict, xmldoc = None): 
	""" 
	Construct an XML document tree representation of a dictionary of 
	frequency series objects containing complex data.  See also 
	read_fseries_xmldoc() for a function to parse the resulting XML 
	documents. 

	If xmldoc is None (the default), then a new XML document is created 
	and the frequency series dictionary added to it.  If xmldoc is not None 
	then the frequency series dictionary is appended to the children of that 
	element inside a new LIGO_LW element. 
	""" 
	if xmldoc is None: 
		xmldoc = ligolw.Document() 
		lw = xmldoc.appendChild(ligolw.LIGO_LW()) 
		for instrument, psd in psddict.items(): 
			fs = lw.appendChild(build_COMPLEX16FrequencySeries(psd)) 
			if instrument is not None: 
				fs.appendChild(param.from_pyvalue(u"instrument", instrument)) 
		return xmldoc

def read_fseries_xmldoc(xmldoc):
	result = dict((param.get_pyvalue(elem, u"instrument"), parse_COMPLEX16FrequencySeries(elem)) for elem in xmldoc.getElementsByTagName(ligolw.LIGO_LW.tagName) if elem.hasAttribute(u"Name") and elem.getAttribute(u"Name") == u"COMPLEX16FrequencySeries") 
	# Interpret empty frequency series as None 
	for instrument in result: 
		if len(result[instrument].data) == 0: 
			result[instrument] = None 
	return result

def make_tseries_xmldoc(psddict, xmldoc = None): 
	""" 
	Construct an XML document tree representation of a dictionary of 
	frequency series objects containing complex data.  See also 
	read_tseries_xmldoc() for a function to parse the resulting XML 
	documents. 

	If xmldoc is None (the default), then a new XML document is created 
	and the frequency series dictionary added to it.  If xmldoc is not None 
	then the frequency series dictionary is appended to the children of that 
	element inside a new LIGO_LW element. 
	""" 
	if xmldoc is None: 
		xmldoc = ligolw.Document() 
		lw = xmldoc.appendChild(ligolw.LIGO_LW()) 
		for instrument, psd in psddict.items(): 
			fs = lw.appendChild(build_REAL8TimeSeries(psd)) 
			if instrument is not None: 
				fs.appendChild(param.from_pyvalue(u"instrument", instrument)) 
		return xmldoc

def read_tseries_xmldoc(xmldoc):
	result = dict((param.get_pyvalue(elem, u"instrument"), parse_REAL8TimeSeries(elem)) for elem in xmldoc.getElementsByTagName(ligolw.LIGO_LW.tagName) if elem.hasAttribute(u"Name") and elem.getAttribute(u"Name") == u"REAL8TimeSeries") 
	# Interpret empty frequency series as None 
	for instrument in result: 
		if len(result[instrument].data) == 0: 
			result[instrument] = None 
	return result
