### selection of largest seqs in server ###

library(data.table)
library(tidyverse)
library(plyr)
library(dplyr)

setwd('/Change/This')

rm(list = ls())

### Import all the ".fai" files from the dorectory ## In the columns the lenght of the sequence can be found.
temp = list.files(pattern="*faa.fai$", ignore.case = F)  ## $ means that stops reading there.
print(temp)

### to arrange all names to match temp and temp 2
temp<- gsub(pattern = ".faa.fai", replacement = ".0", x = temp) 
temp<-sort(temp)
temp<- gsub(pattern = ".0", replacement = ".faa.fai", x = temp)

myfiles = lapply(temp, fread, header =F )

### to arrange all names to match temp and temp 2
temp2 = list.files(pattern="*_df.txt$", ignore.case = F)
temp2<- gsub(pattern = "_df.txt", replacement = ".0", x = temp2) 
temp2<-sort(temp2)
temp2<- gsub(pattern = ".0", replacement = "_df.txt", x = temp2)
myfiles2 = lapply(temp2, fread, sep = " ", fill = T, header = F)

### creating an table for every species with gene id protein id. 
ccds5genes<-list()
human_index<-list()

for (i in 1:length(myfiles2)){
  myfiles2[[i]]$V4<-data.frame(str_remove(myfiles2[[i]]$V4, pattern = "protein_id="))
  #myfiles2[[i]]$V3<-data.frame(str_remove(myfiles2[[i]]$V3, pattern = "GeneID:"))
  myfiles2[[i]]$V3<-data.frame(str_remove(myfiles2[[i]]$V3, pattern = "db_xref="))
  
  ccds5genes[[i]]<-myfiles2[[i]][myfiles2[[i]]$V1 %in% myfiles[[i]]$V1,]
  human_index[[i]]<-merge(myfiles[[i]], ccds5genes[[i]], by.x = "V1", by.y = "V1", all.x = T, all.y = F)
  human_index[[i]]<-human_index[[i]][,c(1,2,7)]
  # human_index$V1.y=NULL
  # human_index$V2.y=NULL
}
head(ccds5genes[[1]])
tail(ccds5genes[[1]])

### keeping genes by geneID only. No other databases. 
for (i in 1:length(ccds5genes)){
  
  ccds5genes[[i]]<- ccds5genes[[i]] %>% 
    mutate(V3 = strsplit(as.character(V3), ",")) %>% 
    unnest(V3)
  
  ccds5genes[[i]]<-ccds5genes[[i]][(ccds5genes[[i]][[3]] %like% "GeneID:"),]  ## the [[3]] = can extract one element from list or data frame, returned object (out of basic object classes) not necessarily list/dataframe
  
}

for (i in 1:length(human_index)){
  
  human_index[[i]]<- human_index[[i]] %>% 
    mutate(V3.y = strsplit(as.character(V3.y), ",")) %>% 
    unnest(V3.y)
  
  human_index[[i]]<-human_index[[i]][(human_index[[i]][[3]] %like% "GeneID:"),]  ## the [[3]] = can extract one element from list or data frame, returned object (out of basic object classes) not necessarily list/dataframe
  
}
####

### Control to test that we only keep genes with GeneID
for (i in 1:length(ccds5genes)) {
if (sum(ccds5genes[[i]][[3]] %like% "GeneID:") == dim(ccds5genes[[i]])[1] ){
  print("yes all good")
  ccds5genes[[i]][[3]]<-(str_remove(ccds5genes[[i]][[3]], pattern = "GeneID:"))
} else {
  print(paste("Still have some other IDs from other databases that are not gene ID or gene ID without GeneID: prefix. Check the list Number:", i), quote = F) 
  sink("./log.WHAT.WENT.WRONG.with.ccds.txt", append = T) # write output to file xxxxx
  print(paste("Still have some other IDs from other databases that are not gene ID or gene ID without GeneID: prefix. Check the list Number:", i), quote = F) 
  sink() # stop recording output
  end
  }
}

for (i in 1:length(human_index)) {
  if (sum(human_index[[i]][[3]] %like% "GeneID:") == dim(human_index[[i]])[1] ){
    print("yes all good")
    human_index[[i]]$V3.y<-(str_remove(human_index[[i]]$V3.y, pattern = "GeneID:"))
  } else {
    sink("./log.WHAT.WENT.WRONG.with.Index.txt", append = T) # write output to file xxxxx
    print(paste("Still have some other IDs from other databases that are not gene ID or gene ID without GeneID: prefix. Check the list Number:", i), quote = F) 
    sink() # stop recording output
    end
  }
}
#####

genesunique<-list()
for (i in 1:length(human_index)){
  # here we select ONLY the largest sequence
  genesunique[[i]]<-human_index[[i]] %>% group_by(V1,V3.y) %>% dplyr::summarise(V5 = max(V2.x))
  colnames(genesunique[[i]])<-c("seqID","GeneID","seqLength")
}

genesunique2<-list() # Eliminating the duplicate genes with same length. 
for (i in 1:length(human_index)){
  genesunique2[[i]]<- genesunique[[i]][!duplicated(genesunique[[i]][[2]]),] 
  }

largeSecMerge<-list() # another way to Eliminate the duplicate genes with same length but arraging by max value
for (i in 1:length(human_index)){
  genesunique[[i]]<-genesunique[[i]][order(genesunique[[i]][[1]], -pmax(genesunique[[i]][[3]])),] 
  rownames(genesunique[[1]])<-genesunique[[1]][[1]]
  largeSecMerge[[i]]<- genesunique[[i]] %>% group_by(GeneID) %>% dplyr::summarise(seqLength= max(seqLength))
}

## control comparing length and similarity of both methods 
for (i in 1:length(genesunique2)) {
  genesunique2[[i]]<-dplyr::arrange(genesunique2[[i]], genesunique2[[i]][[2]])
  if (dim(largeSecMerge[[i]])[1] == dim(genesunique2[[i]])[1] || count((largeSecMerge[[i]][[1]]) == genesunique2[[i]][[2]])) {
  print("All good, you have 0 duplicated genes in both controls", quote = F)
  } else {
    print("error. you have 1 or more duplicated genes in both controls")
    sink("./log.WHAT.WENT.WRONG.with.Index.txt", append = T) # write output to file xxxxx
    print("error. you have 1 or more duplicated genes in both controls")
    sink() # stop recording output
    end
    }
}

paste(temp[1],"LS.txt", sep = "")

for (i in 1:length(genesunique2)){
write.csv(genesunique2[[i]], paste(temp[i],"LS_table.csv", sep = ""))
}

genesunique3<-list()
for (i in 1:length(genesunique2)){
genesunique3[[i]]<-genesunique2[[i]]$seqID
write.table(genesunique3[[i]], paste(temp[i],"LS.txt", sep = ""), row.names = F, col.names = F, quote = F)
}
