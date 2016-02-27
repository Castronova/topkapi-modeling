import pandas as pd
import numpy as np
import os

#Input a folder that has all the folders of names similar to  UT012, Ut027 etc.
path2collectionOfssurgoFolders = r"C:\Users\Prasanna\Box Sync\New Watershed Near RBC\SSURGO_redButteCreekFolder"
path2lookupTable = r"C:\Users\Prasanna\Google Drive\RESEARCH\AutoPTPK2\GREENAMPT_LOOKUPTABLE.csv"
path2lookupTable = os.path.join(os.getcwd(), "GREENAMPT_LOOKUPTABLE.csv")    #have not tested though

lookupTable = pd.read_csv(path2lookupTable , sep=',', skiprows = 0)

#create a list of folders only
folderList = []
[folderList.append(folders) for folders in os.listdir(path2collectionOfssurgoFolders)
    if os.path.isdir(os.path.join(path2collectionOfssurgoFolders, folders))]

for folder in folderList:
    path2ssurgo= path2collectionOfssurgoFolders + "/" + folder
    path2tabular = path2ssurgo+"//tabular"
    path2Spatial= path2ssurgo+"//spatial"


    # Make changes here! The values that we need to average
    valuesToAvg =  ['ksat_r','Ks','dbthirdbar_r','dbfifteenbar_r', 'ResidualWaterContent', 'Porosity',
                    'EffectivePorosity', 'BubblingPressure_Geometric', 'PoreSizeDistribution_geometric'  ]

    fileNameColNoListHeaders = [ ["comp",[1,5,107,108],["ComponentPercent","MajorComponent","MUKEY","COKEY"]],
                                 ["muaggatt",[10,39],["AvaWaterCon","MUKEY"]],
                                 ["chorizon",[6,9,12,81,72,75,169,170],["TopDepth","BottomDepth", "HorizonDepth","ksat_r","dbthirdbar_r","dbfifteenbar_r","COKEY","CHKEY"]],
                                 ["chtextur",[0,2,3],["textureName","CHtxtgrpKEY","CHTXTKEY"]],
                                 ["chtexgrp",[4,5],["CHKEY","CHtxtgrpKEY"]]
                                 ]

    def STEP1_rawToRefined(fileName_ColNoList_Headers, path=path2tabular):
        for afileColHdr in fileName_ColNoList_Headers:
            txtFilename= afileColHdr[0]
            colNo = afileColHdr[1]
            header = afileColHdr[2]

            txtFile = path + "\\" + txtFilename + ".txt"   #RETURNS FULL ADDRESS
            csvFileData = pd.read_csv(txtFile, sep = "|",  header=None, comment='#')

            reqdData = csvFileData.iloc[:,colNo]
            reqdData.columns = header
            reqdData.to_csv(path + "\\" + txtFilename + ".csv", index=False)

        return reqdData

    def STEP2_mergeCSV(path=path2tabular):
        muaggatt  = pd.read_csv(path+"/muaggatt.csv") ; print "/muaggatt.csv", len(muaggatt.index)
        component = pd.read_csv(path+"/comp.csv")    ; print "/comp.csv", len(component.index)
        chorizon = pd.read_csv(path+"/chorizon.csv")  ; print "/chorizon.csv", len(chorizon.index)
        chtextur = pd.read_csv(path+"/chtextur.csv")  ; print "/chtextur.csv", len(chtextur.index)
        chtexgrp = pd.read_csv(path+"/chtexgrp.csv")  ; print "/chtexgrp.csv", len(chtexgrp.index)

        component_Muaggatt =  pd.merge(muaggatt , component, on='MUKEY')
        chorizon_Component_Muaggatt =  pd.merge(component_Muaggatt , chorizon, on='COKEY')

        chTxt_chTxtGrp =  pd.merge(chtextur , chtexgrp, on='CHtxtgrpKEY')
        merged = pd.merge(chTxt_chTxtGrp , chorizon_Component_Muaggatt, on='CHKEY')


        #print chorizonWithComponent
        merged.to_csv(path + "/MERGED.csv", index=False)
        return merged

    #__main__
    try:
        #take necessary columns from the files, and add headers to them
        STEP1_rawToRefined(fileNameColNoListHeaders) ; print "Headers applied to raw txts"
    except Exception, e:
        print e


    try:
        #STEP2 Merge (Chorizon to Component) to Muaggatt ---> result: MERGED.csv
        mergdf = STEP2_mergeCSV() ; print "Merging completed"
    except Exception, e:
        print e


    try:
        #STEP3 Merge lookup table to the LARGE table  ----->result: OverallMergedWithTexture.csv
        mergeWithLookUp = pd.merge(mergdf, lookupTable, on= 'textureName')
        mergeWithLookUp.to_csv(path2tabular + "\\OverallMergedWithTexture.csv", index=False)
        print "Merging with texture lookup table completed"
    except Exception, e:
        print e


    try:
        #STEP4 Take i)Height Weighted Average ii)Component % weighted average --------> result MUKEY-Vs-Values.csv
        merged = pd.read_csv(path2tabular + "\\OverallMergedWithTexture.csv")


        #Caclulation of weighted average
        HorizonDepth2 = merged['BottomDepth'] - merged['TopDepth'] ; merged.loc[:,'HorizonDepth2']= HorizonDepth2

        #the values whose weighted average we want, needs to be given in the list below
        #-------> MUKEY Vs Value (just one) MUKEY-Value.csv
        for valueName in valuesToAvg:       #add those values to merged
            VxD = merged['HorizonDepth2']* merged[valueName] ; merged.loc[:,valueName+"xD_sum"]= VxD
            chorizonCalc = merged.groupby('COKEY').agg({valueName+"xD_sum":np.sum , 'HorizonDepth2':np.sum,'ComponentPercent':np.max,'COKEY':np.max,'MUKEY':np.max })
            chorizonCalc=chorizonCalc.rename(columns = {'HorizonDepth2':'HorizonDepth2_sum'}) #because grouping by cokey, the column name doesnt match its data

            VxD_by_sum = chorizonCalc[valueName+"xD_sum"].astype('float').div(chorizonCalc['HorizonDepth2_sum'].astype('float'))
            chorizonCalc.loc[:,valueName+"_avgH"]= VxD_by_sum

            #percentage weightage
            compPerc_X_Havg = chorizonCalc['ComponentPercent'].astype('float')/100. * chorizonCalc[valueName+"_avgH"]
            chorizonCalc.loc[:,valueName+"_WtAvg"] = compPerc_X_Havg

            #now Group it by MUKEY, and done!
            componentPercentageCalc = chorizonCalc.groupby('MUKEY').agg({'MUKEY':np.max, valueName+"_WtAvg":np.sum })
            componentPercentageCalc.to_csv(path2tabular+"\\MUKEY-"+ valueName  +".csv", index=False)


        #now, function to use the 'valuesToAvg' list above, and merge them against MUKEY
        mukeyValues = componentPercentageCalc.MUKEY

    except Exception, e:
        print e




    try:
        #STEP5: Merge all the MUKEY Vs Values csv --------> result MUKEY-Vs-Values.csv
        lastValueFile = pd.read_csv(path2tabular+"\\MUKEY-"+ valuesToAvg[-1]  +".csv")
        for valueName in valuesToAvg:
            #if valueName == valuesToAvg[-1] : break
            fl = pd.read_csv(path2tabular+"\\MUKEY-"+ valueName  +".csv")
            print path2tabular+"\\MUKEY-"+ valueName  +".csv"
            lastValueFile = pd.merge(lastValueFile, fl, on="MUKEY")

        #print mukeyValuesAllMerged
        lastValueFile.to_csv(path2ssurgo+"\\MUKEY-Vs-Values.csv", index=False)
        print 'All values table written down in the ssurgo folder'

        #create a schema.ini so that arcGIS can understand the MUKEY field
        schema = open(path2ssurgo+"\\schema.ini", "w")
        schema.write("[MUKEY-Vs-Values.csv]"+ "\n" + "Col2=MUKEY Text")  #may not always be column 1 though
        schema.close()

        #delete all the csv files made so far, except the MUKEY-Vs-Values.csv
        filelist = [ f for f in os.listdir("path2tabular") if f.endswith(".csv") ]
        for f in filelist:
            os.remove(f)


    except Exception, e:
        print e



