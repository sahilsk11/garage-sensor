import re
import time
import pprint
#from functools import cmp_to_key

class FusionChart:
    """FusionChart Python Class"""
    
    def __init__(self, chart_type='multi_combi', width=500, height=350, title='', fusion_basedir='/fusioncharts/js') :
        self.chart_type = chart_type
        self.width = width
        self.height = height
        self.fusion_basedir = fusion_basedir
        
        # Set some other defaults. These will typically be set later using setChartProperties
        self.series_data = []
        self.series_attributes = []
        self.categories = []
        self.series_links = []
        self.vlines = {}
        self.hlines = []
        self.listeners = []

        self.color_array = [ "ff9900",   "7951cc",   "ef2f41",   "66cc66",
                                    "c2b00f",   "FFA500",   "A9A9A9",   "E1E1E1",
                                    "00FFFF",   "FFC0CB",   "808080",
                                    "FFFF00",   "000000",
                                    "FF0000",   "0000FF",   "008000",   "CCCCFF",
                                    "FF00FF",   "FFA500",   "A9A9A9",   "E1E1E1",
                                    "00FFFF",   "FFC0CB",   "808080",
                                    "FFFF00",   "000000"]
        
        self.color_array_bugtrends = ["FE0000",   "0000FE",   "00FF01",   "051195",
                "FF00FF",   "FA0D1B",   "A9A9A9",   "E1E1E1",
                "00FFFF",   "FFC0CB",   "808080",
                "FFFF00",   "000000",
                "FF0000",   "0000FF",   "008000",   "CCCCFF",
                "FF00FF",   "FFA500",   "A9A9A9",   "E1E1E1",
                "00FFFF",   "FFC0CB",   "808080",
                "FFFF00",   "000000"]

        # These are some default attributes for the <chart> tag
        # These or any new attribute can be set using setChartAttributes(). 
        # Other useful tags that should be defined by caller:
        # caption xAxisName, yAxisName, PYAxisName, SYAxisName
        self.chart_tag_attributes =  {
                                        "caption": title,
                                        "palette" : 2,
                                        'theme': 'fint',
                                        "showPercentageValues" : 1,
                                        "showValues" : 1,
                                        "formatNumberScale" : 0,
                                        "useRoundEdges" : 0,
                                        "rotateLabels" : 1,
                                        "slantLabels" : 1, 
                                        "showAlternateHGridColor" : 1,
                                        "anchorRadius" : 2,
                                        #"showColumnShadow" : 0,
                                        "animation": 1
                                        }

    # Set attributes for the chart tag
    # Input is a dictionary of attribute value pairs
    def set_chart_tag_attributes (self, params) :
        for attr, value in params.items():
            self.chart_tag_attributes[attr] = value

    def add_listener (self, type, listener) :
        ''' Add a event listener for the chart.
            type: e.g. 'chartClick' OR 'realTimeUpdateComplete'
            listener: Name of a user defined javascript function
        '''
        self.listeners.append((type, listener))

    # Name: add_data_series()
    # Description: Added a data series to the chart.
    # Input Parameters:
    #     series_name: (required) Unique name of this series (string)
    #                  This makes more sense for multiple series data but is currently required for all chart types
    #     series_values: (required) List of values. Should correspond in order with the chart labels (categories).
    #     SERIES_ATTRIBUTES: (optional) Dictionary of attribute/value pair string that will be used
    #                        in the <dataset> tag. Things like color can be overridden using this.
    #                        Currently only applicable to multi-series charts
    #     SERIES_LINKS: (optional) List links.
    #                   Individual data points can be linked to URLs using this. Should be in the same order as values and categories
    def add_data_series (self, series_name, series_values, series_links=[], series_attributes={}):
        # Append a tuple of "name" and "data_list"
        self.series_data.append ((series_name, series_values, series_links, series_attributes))

    def add_category_labels (self, categories):
        self.categories = categories

    # Name: addVlines()
    # Description: Added vertical lines to graph.
    # Input Parameters:
    #     vlines: (required) Dict of labels/attribute
    def add_vlines (self, vlines):
        self.vlines = vlines

    # Name: addHlines()
    # Description: Add horizontal lines to graph.
    # Input Parameters:
    #     HLINE_DATA: (required) Dict of value/attributes
    def add_hlines (self, hlines):
        self.hlines = hlines

    def get_xml (self):
        xml = ''
        chart_type = self.chart_type
        
        chart_tag_attrs = ''
        for attr, value in self.chart_tag_attributes.items():
            chart_tag_attrs = chart_tag_attrs + " %s='%s'" % (attr, value)
    
        # List of chart types: http://www.fusioncharts.com/dev/getting-started/list-of-charts.html
        if (re.match('pie', chart_type, re.I) or re.match('column', chart_type, re.I) or re.match('line', chart_type, re.I) or re.match('area', chart_type, re.I) or re.match('bar', chart_type, re.I) or re.match('doughnut', chart_type, re.I) or re.match('pareto', chart_type, re.I)) :
            # Simple graph, labels and values are together and there is just one data series, pick first
            (series_name, series_values, series_links, series_attributes) = self.series_data[0]

            xml = "<chart " + chart_tag_attrs + " >\n"
            
            for i in range(len(series_values)):
                value = series_values[i]
                # Get the corresponding category label
                label = self.categories[i]
                link_str = ''
                # Check if corresponding link url exists
                if len(series_links) > i:
                    link_str = "link='%s'" % (series_links[i],)
                xml +=  "<set label='%s' value='%s' %s/> \n" % (label, value, link_str)
                i += 1
            xml += "</chart>\n"
        elif (chart_type == 'cylinder'):
            xml = "<chart " + chart_tag_attrs + " >\n"
            (series_name, series_values, series_links, series_attributes) = self.series_data[0]
            xml += "<value>%d</value>" % (series_values)
            xml += "</chart>\n"
        elif (chart_type == 'hlineargauge'):
            ranges = []
            pointers = []
            trendpoints = []
            for series_name, series_values, series_links, series_attributes in self.series_data:
                if series_name == 'ranges':
                    ranges = series_values
                if series_name == 'pointers':
                    pointers = series_values
                if series_name == 'trendpoints':
                    trendpoints = series_values
            xml = "<chart " + chart_tag_attrs + " >\n"
            xml += '<colorrange>'
            for one_range in ranges:
                xml += "<color minvalue='%d' maxvalue='%d' code='%s' label='%s' />" % (one_range['minvalue'], one_range['maxvalue'], one_range['code'], one_range['label'])
            xml += '</colorrange>'
            if len(pointers) > 0:
                xml += '<pointers>'
                for pointer in pointers:
                    xml += "<pointer value='%d' %s />"  % (pointer['value'], pointer.get('attributes', ''))
                xml += '</pointers>'
            if len(trendpoints) > 0:
                xml += '<trendpoints>'
                for trendpoint in trendpoints:
                    xml += "<point startvalue='%d' %s />" % (trendpoint['startvalue'], trendpoint.get('attributes', ''))
                xml += '</trendpoints>'
            xml += "</chart>\n"

        #elif re.match (r'ms', chart_type, re.I) or re.match('zoomline', chart_type, re.I)  or re.match('stack', chart_type, re.I):
        else:
            # Complex graph - usually multiple series with optional secondary Y-axis
            max_value = 0
            one_series = ""
            xml_lineset = ''
            if re.match ('msstack', chart_type):
                # These types require dataset grouping. (so extra dataset tag) TODO: THis needs ot be revisited. Dont think this is working as required
                xml += "<dataset>" 
            counter_series = 0;
            # If there is no data, no point in continuing
            if len(self.series_data) == 0:
                return ''
            for series_name, series_values, series_links, series_attributes in self.series_data:
                dataset_tag = "dataset"
                renderas = "" 
                attributes = ""
                
                for attr_name, attr_value in series_attributes.items():
                    attributes += " %s='%s'" % (attr_name, attr_value)
                    if re.search ('renderas', attr_name, re.I):
                        if (re.search('line', attr_value, re.I) and re.search('stacked', chart_type, re.I)):
                            #dataset_tag = "lineset"
                            # Hmm... dont need to do this anymore?
                            dataset_tag = "dataset"
    
                # Check if color has been overwridden using the series_attribute hash else use the array from chart attributes  
                if ('color' not in series_attributes.keys()) :
                    if len(self.color_array) > 0:
                        attributes += " color='%s'" % self.color_array[counter_series]
                xml_tmp = "<%s seriesName='%s' %s> \n" % (dataset_tag, series_name, attributes)

                for i in range(len(series_values)):
                    value = series_values[i]
                    # Get the corresponding category label
                    label = self.categories[i]
                    link_str = ""
                    # Check if corresponding link url exists
                    if len(series_links) > i:
                        link_str = "link='%s'" % (series_links[i])

                    xml_tmp += "<set value='%s' %s /> \n" % (value, link_str)
                    if (value != '' and value > max_value):
                        max_value = value 
                xml_tmp += "</%s> \n" % (dataset_tag,)
                
                #Linesets need to be added outside of all datasets, so if
                # lineset, keep in a variable to be added later
                if re.search ('lineset', dataset_tag):
                    xml_lineset += xml_tmp
                    counter_series += 1
                else:
                    xml += xml_tmp;
                    counter_series += 1
    
            if re.match ('msstack', chart_type):
                xml += "</dataset>"  
            xml += xml_lineset
    
            # Check if a hline has been specified
            if len(self.hlines) > 0 :
                xml += "<trendLines>"
                for hline_value, attributes in self.hlines():
                    attributes_str = ''
                    for attr_name, attr_value in attributes.items():
                        attributes += " %s='%s'" % (attr_name, attr_value)
                    xml += "<line displayValue='%s' %s />" % (hline_value, attributes)
                xml += "</trendLines>"
    
            xml += "<categories>"
            for category_label in self.categories:
                # Check if a vline has been specified for this label
                if category_label in self.vlines.keys():
                    attributes = ''
                    for attr, value in self.vlines[category_label].items():
                        attributes += " %s='%s'" % (attr, value)
                    xml += "<vline %s/>" % (attributes,)
                xml += "<category label='%s'/> \n" % (category_label)
            xml += "</categories>"
            xml += "</chart>\n"
            
            max_value = int(max_value * 1.1)
            max_value = max_value + 10 - (max_value % 10)
            xml_header = "<chart %s >\n" % (chart_tag_attrs,)
            xml = xml_header + xml
        return (xml); 
    
    # Name: render_chart()
    # Description: Generate the JS code required to render the graph
    #              By default the XML will be generated "inline". For large files, user may want to 
    #              call get_xml directly and save somewhere. The XML_URL can then be passed to this function
    # Input Parameters:
    #       div_id: The id for the div tag to be generated. It should be unique within the HTML doc
    #       XML_URL: (TODO) (optional) The URL where previously generated xml file is stored. If not specified,
    #                it will be automatically generated inline in the HTML  
    #       gen_js_tags: (optional) Whether wrapping <script> tags should be generated
    
    def render_chart (self, div_id, gen_js_tags=True):
        chart_type = self.chart_type
        
        js = ''
        if gen_js_tags:
            js += '<script>\n'
        js += """var chart_id = document.getElementById('myChart_id_%s')
                if (chart_id != null) {
                    chart_id.dispose();
                }
                var myChart_%s = new FusionCharts({
                        id: 'myChart_id_%s',
                        type: '%s', 
                        width: '%s',
                        height: '%s',
                        debugMode : false
                        });\n""" % (div_id, div_id, div_id, chart_type, self.width, self.height)

        for (type, js_func) in self.listeners:
            js += "myChart_%s.addEventListener ('%s', %s);\n" % (div_id, type, js_func)

        str_xml = self.get_xml()
        str_xml = re.sub ("\n", " ", str_xml)
        str_xml = re.sub ('"', '\\"', str_xml)
        js += '''myChart_%s.setXMLData("%s");\n''' % (div_id, str_xml)

        js += "myChart_%s.render('%s');\n" % (div_id, div_id)

        if gen_js_tags:
            js += '</script>\n'

        return (js)
    
   
    def sortfn (self, a, b):
        # Version Strings?
        ma=re.search (r'(\d+)\.(\d+)\.(\d+)\.*(\d*)', a)
        mb=re.search (r'(\d+)\.(\d+)\.(\d+)\.*(\d*)', b)
        if (ma and mb):
            a_padded = ''
            b_padded = ''
            for grp in ma.groups():
                if grp:
                    a_padded += "%03d" % (int(grp))
            for grp in mb.groups():
                if grp:
                    b_padded += "%03d" % (int(grp))
            #a_padded = "%03d%03d%03d%03d" % (int(ma.group(1)),int(ma.group(2)),int(ma.group(3)),int(ma.group(4)))
            #b_padded = "%03d%03d%03d%03d" % (int(mb.group(1)),int(mb.group(2)),int(mb.group(3)),int(mb.group(4)))
            #print "Using $b_padded and $a_padded <br>\n";
            if a_padded > b_padded: return 1
            if a_padded < b_padded: return -1
            return 0
        elif re.search (r'^-?\d+$', a) and re.search (r'^-?\d+$', b): 
            # Numbers
            return int(a) - int(b)
        elif re.search (r'^\d+%$', a) and re.search (r'^\d+%$', b):
            # Percentage
            a = re.sub ('%$', '', a)
            b = re.sub ('%$', '', b)
            return int(a) - int(b)
        elif re.search (r'^#\d+\.', a) and re.search (r'^#\d+\.', b):
            # Numbers added to front of keys for sorting
            a = re.search ('^#(\d+)\.', a).group(1)
            b = re.search ('^#(\d+)\.', b).group(1)
            return int(a) - int(b)
     
        # Normal string compare
        if a > b: return 1
        if a < b: return -1
        return 0

    
