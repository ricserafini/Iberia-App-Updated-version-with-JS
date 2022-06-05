import pandas as pd
import math
import plotly.express as px

class KPIS:
    def criticalIncidents(self, dataframe):
        filter = (dataframe["priority"] == "Critica");
        filteredDf = dataframe[filter];
        return filteredDf.shape[0];
    
    def totalIncidents(self, dataframe):
        return dataframe.shape[0];
    
    def fractionIncidents(self, dataframe):
        counts = dataframe["priority"].value_counts();
        count_dic = counts.to_dict()
        updict = {'Task' : 'Counts of incidents priority'}
        res = {**updict, **count_dic}
        print(res) 
        return res
    
    def backlogPriority(self, dataframe):
        filteredDf = dataframe.query('`incident status` != "Closed" & `incident status` != "Resolved"');
        counts = filteredDf["priority"].value_counts();
        count_dic = counts.to_dict()
        updict = {'Task' : 'Counts of backlog priority'}
        res = {**updict, **count_dic}
        print(res) 
        return res
    
    def incidentTypeBreakdown(self, dataframe):
        counts = dataframe["inc type"].value_counts();
        count_dic = counts.to_dict()
        updict = {'Task' : 'Counts of incident type breakdown'}
        res = {**updict, **count_dic}
        print(res) 
        return res
    
    def criticalMeetsSLA(self, dataframe):
        maxSLAHours = 4;
        filter = (dataframe["priority"] == "Critica");
        filteredDf = dataframe[filter];
        
        filteredDf["create date-time"] = pd.to_datetime(filteredDf["create date-time"], format = "%d/%m/%Y %H:%M");
        filteredDf["resolution date-time"] = pd.to_datetime(filteredDf["resolution date-time"], format = "%d/%m/%Y %H:%M");

        filteredDf["SLATime"] = (filteredDf["resolution date-time"] - filteredDf["create date-time"]).dt.seconds;
        
        # @note https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
        timeSum = filteredDf["SLATime"].sum(axis = 0);
        meetsSLA = 0;
        meetsSLATime = [];
        doesNotMeetSLA = 0;
        doesNotMeetSLATime = [];
        for index, row in filteredDf.iterrows():
            # @note This is in seconds so we compare to seconds
            if (row["SLATime"] <= (maxSLAHours * 60 * 60)):
                meetsSLA += 1;
                meetsSLATime.append(row["SLATime"]);
            else:
                doesNotMeetSLA += 1;
                doesNotMeetSLATime.append(row["SLATime"]);

        if len(meetsSLATime) > 0:
            meetsSLATime = sum(meetsSLATime) / len(meetsSLATime);
            # @note To hours as float
            meetsSLATime = (meetsSLATime / 60) / 60;
            meetsSLATimeMinsRem = float(meetsSLATime) - math.floor(meetsSLATime);
            meetsSLATimeMinsRem = meetsSLATimeMinsRem * 60;
            finalMeetsSLAString = str(math.floor(meetsSLATime)) + " hours and " + str(round(meetsSLATimeMinsRem)) + " minutes";
        else:
            finalMeetsSLAString = "No incidents to report under these conditions";
        
        if len(doesNotMeetSLATime) > 0:
            doesNotMeetSLATime = sum(doesNotMeetSLATime) / len(doesNotMeetSLATime);
            # @note To hours as float
            doesNotMeetSLATime = (doesNotMeetSLATime / 60) / 60;
            doesNotMeetSLATimeMinsRem = float(doesNotMeetSLATime) - math.floor(doesNotMeetSLATime);
            doesNotMeetSLATimeMinsRem = doesNotMeetSLATimeMinsRem * 60;
            finalDoesNotMeetSLAString = str(math.floor(doesNotMeetSLATime)) + " hours and " + str(round(doesNotMeetSLATimeMinsRem)) + " minutes";
        else:
            finalDoesNotMeetSLAString = "No incidents to report under these conditions";
            
        return {"chart": {'Task' : 'Counts of meet and not SLA',"Meets SLA":meetsSLA,"Does NOT meet SLA":doesNotMeetSLA}, "timings": {"meets": finalMeetsSLAString, "doesnot": finalDoesNotMeetSLAString}};
    
    def custom(self, dataframe):
        counts = dataframe["incident status"].value_counts(dropna = False);
        count_dic = counts.to_dict()
        updict = {'Task' : 'custom KPIs'}
        res = {**updict, **count_dic}
        print(res) 
        return res

def getKpis(db, db_backlog):
    stats = KPIS();
    criticalSLAData = stats.criticalMeetsSLA(db);
    criticalIncidents = stats.criticalIncidents(db);
    totalIncidents = stats.totalIncidents(db);
    incidentTypeBreakdownFraction = stats.fractionIncidents(db);
    backlogTypeBreakdown = stats.backlogPriority(db_backlog);
    incidentTypeBreakdown = stats.incidentTypeBreakdown(db);
    p1SLAResolutionTime = criticalSLAData["chart"];
    p1AverageTimeSLA = criticalSLAData["timings"]["meets"]
    p1AverageTimeNotSLA = criticalSLAData["timings"]["doesnot"];
    incidentStatusType =  stats.custom(db)
    return criticalSLAData,criticalIncidents,totalIncidents,incidentTypeBreakdownFraction,backlogTypeBreakdown,incidentTypeBreakdown,p1SLAResolutionTime,p1AverageTimeSLA,p1AverageTimeNotSLA,incidentStatusType

def getThrends():
    stats = KPIS();
    db_jan = pd.read_csv("data/2101.csv");
    db_feb = pd.read_csv("data/2102.csv");
    db_march = pd.read_csv("data/2103.csv");
    db_april = pd.read_csv("data/2104.csv");

    totalIns = {'Task' : 'count', "January": stats.totalIncidents(db_jan), "February": stats.totalIncidents(db_feb), "March": stats.totalIncidents(db_march), "April": stats.totalIncidents(db_april)}
    totalCriticalIns = {'Task' : 'count', "January": stats.criticalIncidents(db_jan), "February": stats.criticalIncidents(db_feb), "March": stats.criticalIncidents(db_march), "April": stats.criticalIncidents(db_april)}
    return totalIns,totalCriticalIns