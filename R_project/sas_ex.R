rm(list=ls(all=TRUE))
library("haven")
library("survey")
library(dplyr)
require(data.table)
chs20<-read_sas("data/chs2020_public.sas7bdat")

#city-wide estimates
chs<-transform(chs20,strata=as.character(strata),all=as.factor(survey))

#define the survey
chs.dsgn<-svydesign(ids = ~1,strata = ~strata,weights=~wt21_dual,data = chs,nest = TRUE,na.rm=TRUE )
#age adjusted survey
pop.agecat4=c(0.128810, 0.401725, 0.299194, 0.170271)
chs.stdes<-svystandardize(subset(chs.dsgn,diabetes20>0 ),by=~agegroup,over=~all,population=pop.agecat4,excluding.missing =~ agegroup+ ~all)

#weighted N
aggregate(chs20$wt21_dual, by=list(Category=chs20$diabetes20), FUN=sum)

#crude prevalance estimates
svyby(~diabetes20==1,~all,subset(chs.dsgn,diabetes20>0),svyciprop,vartype = "ci",method="xlogit",df=degf(chs.dsgn))
svyby(~diabetes20==2,~all,subset(chs.dsgn,diabetes20>0),svyciprop,vartype = "ci",method="xlogit",df=degf(chs.dsgn))

#age adjusted prevalance estimates

svyby(~diabetes20==1,~all,chs.stdes,svyciprop,vartype = "ci",method="xlogit",df=degf(chs.dsgn))
svyby(~diabetes20==2,~all,chs.stdes,svyciprop,vartype = "ci",method="xlogit",df=degf(chs.dsgn))

#estimate by sex
chs<-transform(chs20,strata=as.character(strata),allsex2=as.factor(birthsex))

#define the survey
chs.dsgn<-svydesign(ids = ~1,strata = ~strata,weights=~wt21_dual,data = chs,nest = TRUE,na.rm=TRUE )
#age adjusted survey
pop.agecat4=c(0.128810, 0.401725, 0.299194, 0.170271)
chs.stdes<-svystandardize(subset(chs.dsgn,diabetes20>0 ),by=~agegroup,over=~allsex2,population=pop.agecat4,excluding.missing =~ agegroup+ ~allsex2)

#crude prevalance estimates
svyby(~diabetes20==1,~allsex2,subset(chs.dsgn,diabetes20>0),svyciprop,vartype = "ci",method="xlogit",df=degf(chs.dsgn))
svyby(~diabetes20==2,~allsex2,subset(chs.dsgn,diabetes20>0),svyciprop,vartype = "ci",method="xlogit",df=degf(chs.dsgn))


#age adjusted prevalance estimates

svyby(~diabetes20==1,~allsex2,chs.stdes,svyciprop,vartype = "ci",method="xlogit",df=degf(chs.dsgn))
svyby(~diabetes20==2,~allsex2,chs.stdes,svyciprop,vartype = "ci",method="xlogit",df=degf(chs.dsgn))
