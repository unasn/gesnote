"""
Definition of views.
"""

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from itertools import islice
from datetime import datetime, timedelta
from notes3.models import Anonymat, Examen, Moyenne_tmp_cmtp,Statut_info,Link_cm_td,Dispaching,Moyenne_Ue,Moyenne_ecue_cm,Moyenne_ue_cm,Moyenne_ue_tp,Resultat_examen_cmtp,Sexe, anotmp, equivalence, tmp_inscr, BigUeCat,Niveau_from_to, Resultat_bigcat, Composition, Moyenne_ue_cmtp, Compotype, Niveau,moyenne_ecue, moyenne_ecue_tmp, Filiere, Ue, AnUniv, UeInfo, Anonymat, Etudiant, UeCat, Resultat_semestre
from notes3.models import Inscription, err_inscription, Historic, Notes_ecue, Notes_Ue, Salle, Enseignant, Resultat_semestre, Heures, Resultat, Resultat_uecat, Resultat_grade, Resultat_info
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from notes3.forms import examform, rexamform,iForms, iForms2, iupForms,compoform,anoform,AnUnivform,InscrForm, upnote,ecueform, addnote, tdtp_notesform, addecueform, formlisting, ueAddform, notesform,tnoteform, oneanoform, salleform, enseigform, horaireform, etform,CetudiantForm, etudiantForm, formprint,ueform
from django.urls import reverse_lazy
from django.urls import reverse
from django.core.mail import send_mail,EmailMessage
from django.db.models import Q, Count, Sum, Max, Min, F,Subquery, OuterRef
import openpyxl
from notes3.models import tmpnote
from pyexcel_ods import get_data
import io
import math
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, A3, inch, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, \
    Spacer, Table, TableStyle, PageBreak,Frame,BaseDocTemplate
import csv,random
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import connection
from pyexcel_ods import get_data
from reportlab.graphics.shapes import Rect,String,Polygon,Drawing
from django.db.models import IntegerField, Sum, Case, When
import os

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    au_id=get_object_or_404(AnUniv,Q(curau=True))
    examlist=Examen.objects.filter(Q(anuniv=au_id) &  Q(delib_cm__isnull=False))
    for ex in examlist:
        nbetudiant=Notes_Ue.objects.filter(examen=ex).count()
        ex.nbetudiant=nbetudiant
        admis=Resultat_info.objects.get(id=1)
        nbadmis=Notes_Ue.objects.filter(Q(examen=ex) & Q(resultat=admis)).count()
        ex.nbadmis=nbadmis
        #ex.pourcreussite=round((100*nbadmis/nbetudiant),2)
        ex.save()
    aulist=AnUniv.objects.filter(auid__gte=1718)
    
    return render(
        request,
        'notes3/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
            'auid':aulist,
            'curau':au_id.auid,
        }
    )



def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'notes3/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
            
        }
    )


class filiere(ListView):
    model=Filiere
    template_name='notes3/filiere_list.html'
    def get_context_data(self, **kwargs):
        context=super(filiere,self).get_context_data(**kwargs)
        aid=self.kwargs['anuniv']
        anuniv=AnUniv.objects.get(auid=aid)
        fil=Filiere.objects.filter(anuniv=anuniv)
        fcount=Filiere.objects.filter(anuniv=anuniv).count()
        context['filieres']=fil
        context['curau']=aid
        context['fcount']=fcount
        return context

class niveaudetail(DetailView):
    model=Niveau
    slug_field='nivid'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        niveau=self.object
        anuniv=niveau.filiere.anuniv
        eff=Inscription.objects.filter(Q(niveau=niveau) & Q(anuniv=anuniv)).count()
        niveau.effectif=eff
        niveau.save()
        nbreues=Ue.objects.filter(Q(niveau=niveau)).count()
        exam_nbre1=Examen.objects.filter(Q(anuniv=anuniv) & Q(niveau=niveau) & Q(session=1)).count()
        exam_nbre2=Examen.objects.filter(Q(anuniv=anuniv) & Q(niveau=niveau) & Q(session=2)).count()
        exam_del1=Examen.objects.filter(Q(anuniv=anuniv) & Q(niveau=niveau) & Q(session=1) & Q(calcul=True)).count()
        exam_del2=Examen.objects.filter(Q(anuniv=anuniv) & Q(niveau=niveau) & Q(session=2) & Q(calcul=True)).count()
        print(exam_nbre1)
        context['session1']=exam_nbre1
        context['session2']=exam_nbre2
        context['ues']=nbreues
        context['achev1']=exam_del1
        context['achev2']=exam_del2
        return context

class nivano_update(UpdateView):
    model=Niveau
    slug_field='nivid'
    fields=['minano','maxano','nbrecopy']
    template_name_suffix='_update_form'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        niveau=self.object
        
        context['typedoc']=1
        context['effectif']=niveau.effectif
        
        return context
    def get_initial(self):
        initial=super(nivano_update, self).get_initial()
        initial=initial.copy()
        niveau=self.object
        ues=Ue.objects.filter(Q(niveau=niveau))
        somme=0
        for ue in ues:
            nbreecues=UeInfo.objects.filter(Q(niveau=niveau) & Q(ecue_ignored=False) & Q(ue=ue)).count()
            somme=somme+niveau.effectif*nbreecues
        nbrecopie=somme+math.floor(somme/2)
        minano=int(math.floor(int(str(niveau.nivid)[:-2])*math.pow(10,len(str(nbrecopie)))))
        initial['minano']=minano
        initial['maxano']=minano+nbrecopie
        initial['nbrecopy']=nbrecopie
        return initial
    def get_success_url(self):
        
        return reverse('nivdetail',args=(int(self.object.nivid),))
def check_marges(request):
    minano=request.GET.get("minano")
    maxano=request.GET.get("maxano")
    rge=list(range(int(minano),int(maxano)))
    nivs=Niveau.objects.all()
    overlay=False
    nbre=0
    nivlist=[]
    for n in nivs:
        if n.minano!=None:
            nivrge=list(range(n.minano,n.maxano))
            for i in rge:
                if i in nivrge:
                    nbre+=1
                    overlay=True
                    nivlist.append(n)
                else:
                    overlay= False
    context={}
    context['ano']=minano
    context['overlay']=overlay
    context['nombre']=nbre
    return JsonResponse(context)



class niveau_list(ListView):
    model=Niveau
    template_name='notes3/niveau_list.html'
    
    def get_context_data(self, **kwargs):
        context=super(niveau_list,self).get_context_data(**kwargs)
        fid=self.kwargs['filid']
        fil=Filiere.objects.get(filid=fid)
        context['niveaux']=Niveau.objects.filter(filiere=fil).order_by('nivid')
        context['filiere']=fid
        nivcount=Niveau.objects.filter(filiere=fil).count()
        context['nivcount']=nivcount
        au_id=get_object_or_404(AnUniv,Q(curau=True))
        context['curau']=fil.anuniv.auid
        return context

class Niveaux_update(UpdateView):
    model=Niveau
    slug_field='nivid'
    fields=['minao','maxano','effectif']
    template_name_suffix='_update_form'


class bigcat_resultat_list(ListView):
    model=Resultat_bigcat
    template_name='notes3/bigcat_resultat.html'
    def get_context_data(self,**kwargs):
        context=super(bigcat_resultat_list,self).get_context_data(**kwargs)
        nivid=self.kwargs['nivid']
        niveau=Niveau.objects.get(nivid=nivid)
        auid=niveau.filiere.anuniv.auid
        etudiantid=self.kwargs['etudiantid']
        etudiant=Etudiant.objects.get(etudiantid=etudiantid)
        context['data']=Resultat_bigcat.objects.filter(Q(niveau=niveau) & Q(etudiant=etudiant))
        context['etudiant']=etudiant
        context['niveau']=niveau
        
        curau=get_object_or_404(AnUniv,Q(curau=True))
        print(curau)
        
        context['curau']=curau.auid
        return context

class AddExamen(CreateView):
    model=Examen
    template_name='notes3/examen_create.html'
    success_url=reverse_lazy('examlist')
    form_class=examform
    def get_initial(self):
        initial=super(AddExamen, self).get_initial()
        initial=initial.copy()
        niveau=Niveau.objects.get(nivid=self.kwargs['nivid'])
        initial['anuniv']=niveau.filiere.anuniv.auid
        initial['niveau']=self.kwargs['nivid']
        initial['calcul']=False
        return initial
    def get_success_url(self):
        nivid=self.kwargs['nivid']
        return reverse_lazy( 'nivdetail', kwargs={'slug': nivid})



    
class rAddExamen(CreateView):
    model=Examen
    template_name='notes3/examen_rcreate.html'
    success_url=reverse_lazy('examlist')
    form_class=rexamform
    def get_initial(self):
        initial=super(rAddExamen, self).get_initial()
        initial=initial.copy()
        initial['calcul']=False
        initial['niveau']=self.kwargs['nivid']
        max_id=Examen.objects.aggregate(max=Max('id'))
        return initial
    def get_success_url(self):
        nivid=self.kwargs['nivid']
        return reverse_lazy( 'listue',kwargs={'niveauid': nivid})
    

def uelist(request):
    niv=request.GET.get('niveau_id')
    session=request.GET.get('session')
    niveau=Niveau.objects.get(nivid=niv)
    deja=Examen.objects.filter(Q(niveau=niveau) & Q(anuniv=AnUniv.objects.get(curau=True)) & Q(session=session)).values('ue')
    uelist=Ue.objects.filter(niveau=niveau).exclude(ueid__in=deja).order_by('code')
    return render(request, 'notes3/ue_list.html', {'ue_list':uelist})

def xexamlist(request):
    ueid=request.GET.get('ue_id')
    ue=Ue.objects.get(ueid=ueid)
    exams=Examen.objects.filter(ue=ue).order_by('anuniv','session')
    return render(request,'notes3/xexamlist.html',{'exam':exams})


class examenlist(ListView):
    model=Examen
    template_name='notes3/examen_list.html'
    context_object_name='examens'
    def get_context_data(self, **kwargs):
        context=super(examenlist,self).get_context_data(**kwargs)
        nivid=self.kwargs['nivid']
        session=self.kwargs['session']
        niv=Niveau.objects.get(nivid=nivid)
        context['examens']=Examen.objects.filter(Q(niveau=niv) & Q(anuniv=niv.filiere.anuniv) & Q(session=session)).order_by('ue__semestre')
        context['niveau']=niv
        context['curau']=niv.filiere.anuniv.auid
        context['session']=session

        return context

class deletexamen(DeleteView):
    model=Examen
    slug_field='id'
    def get_success_url(self):
        niveau=self.object.niveau
        return reverse_lazy( 'examlist', kwargs={'nivid': niveau.nivid,'session':self.object.session})
class deleteinscription(DeleteView):
    model=Inscription
    slug_field='id'
    def get_success_url(self):
        niveau=self.object.niveau
        return reverse_lazy('linscrire',kwargs={'niveauid':niveau.nivid})

class examendetail(DetailView):
    model=Examen
    slug_field='id'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['composition']=Composition.objects.filter(examen=self.object.id)
        comp_count=Composition.objects.filter(examen=self.object.id).count()
        tp=Compotype.objects.get(id=3)
        td=Compotype.objects.get(id=2)
        cm=Compotype.objects.get(id=1)
        comptp=Composition.objects.filter(Q(examen=self.object) & Q(comptype=tp)).count()
        comptd=Composition.objects.filter(Q(examen=self.object) & Q(comptype=td)).count()
        compcm=Composition.objects.filter(Q(examen=self.object) & Q(comptype=cm)).count()
        examen=self.object
        curau=get_object_or_404(AnUniv,Q(curau=True))
        context['curau']=curau.auid

        if self.object.afficher==True:
            list_ajourne_ecue(self.object.id)
        if self.object.session==2:
            list_ajourne_ecue(self.object.id)
        if examen.session==1:
            try:
                exam_ses2=get_object_or_404(Examen,Q(niveau=examen.niveau) & Q(ue=examen.ue) & Q(session=2) & Q(anuniv=curau))
                context['exses2']=exam_ses2
            except:
                context['exses2']=None
        if examen.session==2:
            try:
                exam_ses2=get_object_or_404(Examen,Q(niveau=examen.niveau) & Q(ue=examen.ue) & Q(session=1) & Q(anuniv=curau))
                context['exses2']=exam_ses2
            except:
                context['exses2']=None
        texam=self.object.niveau.tp
        context['comptp']=comptp
        context['texam']=texam
        examen.nbtp=comptp
        examen.nbtd=comptd
        examen.nbcm=compcm
        checkcoef_calcmode(self.object.id)
        context['calcmode']=examen.calcmode
        return context

class examen_update(UpdateView):
    model=Examen
    slug_field='id'
    fields=['ecue_ignored','afficher','calcmode']
    template_name_suffix='_update_form'

class examen_afficher(UpdateView):
    model=Examen
    slug_field='id'
    fields=['afficher']
    template_name_suffix='update_form'

class composition_list(ListView):
    model=Composition
    template_name="notes3/examen_detail.html"
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        examid=self.kwargs['examid']
        examen=Examen.objects.get(id=examid)
        compositions=Composition.objects.filter(examen=examen)
        context['composition']=compositions
        return context


class compositioncreate(CreateView):
    model=Composition
    form_class=compoform
    def get_initial(self, **kwargs):
        initial=super(compositioncreate, self).get_initial()
        initial=initial.copy()
        examenid=self.kwargs['examid']
        examen=Examen.objects.get(id=examenid)
        admis=Resultat_info.objects.get(id=1)
        dejaadmis=Notes_Ue.objects.filter(Q(resultat=admis) & Q(examen__ue__code=examen.ue.code) & Q(examen__niveau__code=examen.niveau.code)).values('etudiant')
        nbetud=Inscription.objects.filter(Q(niveau=examen.niveau) & Q(anuniv=examen.anuniv)).exclude(etudiant__in=dejaadmis)
        compcount=Composition.objects.filter(Q(examen__niveau=examen.niveau) & Q(examen__anuniv=examen.anuniv)).count()
        if compcount>0:
            maxan=Composition.objects.filter(Q(examen__niveau=examen.niveau) & Q(examen__anuniv=examen.anuniv)).aggregate(maxan=Max('lano'))
            if nbetud.count()*0.3<1:
                initial['fano']=maxan['maxan']+5
            else:

                initial['fano']=maxan['maxan']+int(math.floor(nbetud.count()*0.3))
        else:
            fano=examen.niveau.minano
            initial['fano']=fano
        initial['examen']=self.kwargs['examid']
        initial['effectif']=nbetud.count()
        initial['session']=examen.session
        
        return initial
    def get_success_url(self):
        examid=self.kwargs['examid']
        examen=Examen.objects.get(id=examid)
        return reverse_lazy('detexam', kwargs={'slug': examen.id})


def get_ecue_effectif(request):
    ecueid=request.GET.get("ecueid")
    examenid=request.GET.get("examenid")
    examen=Examen.objects.get(id=examenid)
    ecue=UeInfo.objects.get(uei=ecueid)
    examen1=get_object_or_404(Examen,Q(session=1) & Q(ue__code=examen.ue.code) & Q(anuniv=examen.anuniv) & Q(niveau=examen.niveau))

    cm=Compotype.objects.get(id=1)
    admis=Resultat_info.objects.get(id=1)
    compos1=get_object_or_404(Composition,Q(examen__session=1) & Q(ecue__code=ecue.code) & Q(examen__anuniv=examen.anuniv) & Q(comptype=cm) & Q(examen__niveau=examen.niveau))
    dejaca=Notes_ecue.objects.filter(Q(note__gte=10) & Q(composition=compos1)).values('etudiant')
    dejaadmis=Notes_Ue.objects.filter(Q(resultat=admis) & Q(examen__ue__code=examen.ue.code) & Q(examen__niveau__code=examen.niveau.code)).values('etudiant')
    et=Inscription.objects.filter(Q(niveau=examen.niveau) & Q(anuniv=examen.niveau.filiere.anuniv)).exclude(etudiant__in=dejaadmis).values('etudiant')
    et=et.exclude(etudiant__in=dejaca)
    context={}
    context['effectif']=et.count()
    return JsonResponse(context)
    




#Fonction de report des notes des composition avec tous étudiants admis
def report_notes_examen(examid):
    examen=Examen.objects.get(id=examid)
    au=AnUniv.objects.filter(curau=True)
    exam_ses1=Examen.objects.filter(Q(niveau=examen.niveau) & Q(ue=examen.ue) & Q(session=1) & Q(afficher=True))
    
    if exam_ses1:
        for ex in  exam_ses1:
            
            if ex.reporter==False or ex.reporter==None:
                ajourne=Resultat_info.objects.get(id=3)
                et_ajour=Notes_Ue.objects.filter(Q(examen=ex) & Q(resultat=ajourne)).values('etudiant')
                td=Compotype.objects.get(id=2)
                compos=Composition.objects.filter(examen=ex).exclude(comptype=td)
                
                for c_ses1 in compos:
                    
                    c_ses2=Composition.objects.filter(Q(ecue=c_ses1.ecue) & Q(examen__session=2) & Q(comptype=c_ses1.comptype) & Q(examen=examen))
                    if c_ses2:
                        for c2 in c_ses2:
                            etud_note_gte=Notes_ecue.objects.filter(Q(composition=c_ses1) & Q(note__gte=10) & Q(etudiant__in=et_ajour)).values('etudiant')
                            if c_ses1.ano==True:
                                saisi_ses2=Anonymat.objects.filter(composition=c2).values('etudiant')
                                Anonymat.objects.filter(Q(composition=c_ses1) & Q(etudiant__in=etud_note_gte)).exclude(etudiant__in=saisi_ses2).update(composition=c2)
                                Anonymat.objects.filter(Q(composition=c_ses1) & Q(etudiant__in=etud_note_gte)).exclude(etudiant__in=saisi_ses2).update(reporter=True)            
                            existdeja=Notes_ecue.objects.filter(Q(composition=c2) & Q(etudiant__in=et_ajour)).values('etudiant')
                            Notes_ecue.objects.filter(Q(composition=c_ses1) & Q(note__gte=10) & Q(etudiant__in=et_ajour)).exclude(etudiant__in=existdeja).update(reporter=True)
                            Notes_ecue.objects.filter(Q(composition=c_ses1) & Q(note__gte=10) & Q(etudiant__in=et_ajour)).exclude(etudiant__in=existdeja).update(examen=examen)
                            Notes_ecue.objects.filter(Q(composition=c_ses1) & Q(note__gte=10) & Q(etudiant__in=et_ajour)).exclude(etudiant__in=existdeja).update(composition=c2)
                    else:
                        etud_note_gte=Notes_ecue.objects.filter(Q(composition=c_ses1) & Q(note__gte=10) & Q(etudiant__in=et_ajour)).values('etudiant')
                        c2=Composition.objects.create(
                            ecue=c_ses1.ecue,
                            examen=examen,
                            comptype=c_ses1.comptype,
                            ano=c_ses1.ano,
                            ecue_ignored=c_ses1.ecue_ignored
                        )
                        c2.save()
                        if c_ses1.ano==True:
                                saisi_ses2=Anonymat.objects.filter(composition=c2).values('etudiant')
                                Anonymat.objects.filter(Q(composition=c_ses1) & Q(etudiant__in=etud_note_gte)).exclude(etudiant__in=saisi_ses2).update(composition=c2)
                                Anonymat.objects.filter(Q(composition=c_ses1) & Q(etudiant__in=etud_note_gte)).exclude(etudiant__in=saisi_ses2).update(reporter=True)            
                        existdeja=Notes_ecue.objects.filter(Q(composition=c2) & Q(etudiant__in=et_ajour)).values('etudiant')
                        Notes_ecue.objects.filter(Q(composition=c_ses1) & Q(note__gte=10) & Q(etudiant__in=et_ajour)).exclude(etudiant__in=existdeja).update(reporter=True)
                        Notes_ecue.objects.filter(Q(composition=c_ses1) & Q(note__gte=10) & Q(etudiant__in=et_ajour)).exclude(etudiant__in=existdeja).update(examen=examen)
                        Notes_ecue.objects.filter(Q(composition=c_ses1) & Q(note__gte=10) & Q(etudiant__in=et_ajour)).exclude(etudiant__in=existdeja).update(composition=c2)
         
            ex.reporter=True
            ex.save()

#Fonction de report des notes
def report_notes(compid):
    comp_ses2=Composition.objects.get(compid=compid)
    ecue=comp_ses2.ecue
    exam_ses2=comp_ses2.examen
    exam_ses1=Examen.objects.filter(Q(niveau=exam_ses2.niveau) & Q(ue=exam_ses2.ue) & Q(session=1) & Q(afficher=True))
    ajourne=Resultat_info.objects.get(id=3)
    admis=Resultat_info.objects.get(id=1)
    

    if exam_ses1:
        for ex in  exam_ses1:
            #Recomposition
            etadmis=Notes_Ue.objects.filter(Q(examen=ex) & Q(resultat=admis)).values('etudiant')
            etcomp=Notes_ecue.objects.filter(Q(examen=exam_ses2) & Q(etudiant__in=etadmis)).values('etudiant') 
            recomposition=Resultat_info.objects.get(id=6)
            Notes_Ue.objects.filter(Q(examen=ex) & Q(etudiant__in=etcomp)).update(resultat=recomposition)
            #fin
            et_ajour=Notes_Ue.objects.filter(Q(examen=ex) & Q(resultat=ajourne)|Q(resultat=recomposition)).values('etudiant')
            admis_sess1=Notes_Ue.objects.filter(Q(examen=ex) & Q(resultat=admis)).values('etudiant')
            
            if ex.ecue_ignored==False:
                td=Compotype.objects.get(id=2)
                compos=Composition.objects.filter(Q(examen=ex) & Q(ecue=ecue) & Q(comptype=comp_ses2.comptype)).exclude(comptype=td)
                for c_ses1 in compos:
                   
                    etud_note_gte=Notes_ecue.objects.filter(Q(composition=c_ses1) & Q(note__gte=10) & Q(etudiant__in=et_ajour)).values('etudiant')
                    if c_ses1.ano==True:
                        saisi_ses2=Anonymat.objects.filter(composition=comp_ses2).values('etudiant')
                        Anonymat.objects.filter(Q(composition=c_ses1) & Q(etudiant__in=etud_note_gte)).exclude(etudiant__in=saisi_ses2).update(composition=comp_ses2)
                        Anonymat.objects.filter(Q(composition=c_ses1) & Q(etudiant__in=etud_note_gte)).exclude(etudiant__in=saisi_ses2).update(reporter=True)
                    
                    existdeja=Notes_ecue.objects.filter(Q(composition=comp_ses2) & Q(etudiant__in=et_ajour)).values('etudiant')
                    Notes_ecue.objects.filter(Q(composition=c_ses1) & Q(note__gte=10) & Q(etudiant__in=et_ajour)).exclude(etudiant__in=existdeja).update(reporter=False)
                    Notes_ecue.objects.filter(Q(composition=c_ses1) & Q(note__gte=10) & Q(etudiant__in=et_ajour)).exclude(etudiant__in=existdeja).update(reporter=True)
                    Notes_ecue.objects.filter(Q(composition=c_ses1) & Q(note__gte=10) & Q(etudiant__in=et_ajour)).exclude(etudiant__in=existdeja).update(examen=exam_ses2)
                    Notes_ecue.objects.filter(Q(composition=c_ses1) & Q(note__gte=10) & Q(etudiant__in=et_ajour)).exclude(etudiant__in=existdeja).update(composition=comp_ses2)
                    c_ses1.reporter=True
                    c_ses1.save()

            if ex.ecue_ignored==True:
                tp=Compotype.objects.get(id=3)
                td=Compotype.objects.get(id=2)
                compos=Composition.objects.filter(Q(examen=ex) & Q(ecue=ecue) & Q(comptype=tp))
                nbtp=compos.count()
                if nbtp==0:   
             
                    compos=Composition.objects.filter(Q(examen=ex) & Q(comptype=tp))
                    nbtp=compos.count()
                if nbtp>0:
                    compos=Composition.objects.filter(Q(examen=ex) &  Q(comptype=comp_ses2.comptype)).exclude(comptype=td)
                   
                    for c_ses1 in compos:
                       
                        etud_note_gte=Notes_ecue.objects.filter(Q(composition=c_ses1) & Q(note__gte=10) & Q(etudiant__in=et_ajour)).values('etudiant')
                        if c_ses1.ano==True:
                            saisi_ses2=Anonymat.objects.filter(composition=comp_ses2).values('etudiant')
                            Anonymat.objects.filter(Q(composition=c_ses1) & Q(etudiant__in=etud_note_gte)).exclude(etudiant__in=saisi_ses2).update(composition=comp_ses2)
                            Anonymat.objects.filter(Q(composition=c_ses1) & Q(etudiant__in=etud_note_gte)).exclude(etudiant__in=saisi_ses2).update(reporter=True)
                        existdeja=Notes_ecue.objects.filter(Q(composition=comp_ses2) & Q(etudiant__in=et_ajour)).values('etudiant')
                        Notes_ecue.objects.filter(Q(composition=c_ses1) & Q(note__gte=10) & Q(etudiant__in=et_ajour)).exclude(etudiant__in=existdeja).update(reporter=True)
                        Notes_ecue.objects.filter(Q(composition=c_ses1) & Q(note__gte=10) & Q(etudiant__in=et_ajour)).exclude(etudiant__in=existdeja).update(examen=exam_ses2)
                        Notes_ecue.objects.filter(Q(composition=c_ses1) & Q(note__gte=10) & Q(etudiant__in=et_ajour)).exclude(etudiant__in=existdeja).update(composition=comp_ses2)
                        c_ses1.reporter=True
                        c_ses1.save()

def ecue_list(request):
    examen_id=request.GET.get('examen')
    cid=request.GET.get('comptype')
    examen=Examen.objects.get(id=examen_id)
    niveau=examen.niveau
    ue=examen.ue
    ecue_ignored=examen.ecue_ignored
    if cid == None:
        cid=1
    comptype=Compotype.objects.get(id=cid)
    tp=Compotype.objects.get(id=3)
    dejasaisi=Composition.objects.filter(Q(examen=examen)).values_list('ecue__uei')
    if comptype==tp:
        ecue=UeInfo.objects.filter(Q(niveau=niveau) & Q(ue=ue))
    else:
        ecue=UeInfo.objects.filter(Q(niveau=niveau) & Q(ue=ue) & Q(ecue_ignored=ecue_ignored))
    return render(request,'notes3/ecue_list.html',{'ecue_list':ecue})

def simple_ecue_list(request):
    ueid=request.GET.get('ueid')
  
    ue=Ue.objects.get(ueid=ueid)
    ecue=UeInfo.objects.filter(ue=ue)


    return render(request,'notes3/simple_ecue_list.html', {'ecue':ecue})
class composition_delete(DeleteView):
    model=Composition
    slug_field='compid'
    def delete(self, request, *args, **kwarg):
        self.object=self.get_object()
        
        note_ecue=Notes_ecue.objects.filter(composition=self.object)
        note_ecue.delete()
        tnote=tmpnote.objects.filter(composition=self.object)
        tnote.delete()
        note_ue=Notes_Ue.objects.filter(examen=self.object.examen)
        note_ue.delete()
        lct=Link_cm_td.objects.filter(linked_td=self.object)
        print(lct)
        lct.delete()
        ano=Anonymat.objects.filter(composition=self.object)
        ano.delete()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)
    def get_success_url(self,  **kwargs):
        return reverse_lazy('examlist', kwargs={'nivid': self.object.examen.niveau.nivid,'session':self.object.examen.session})

class commposition_update(UpdateView):
    model=Composition
    slug_field='compid'
    form_class=compoform
    template_name_suffix='_update_form'
    def get_success_url(self,  **kwargs):
        return reverse_lazy('examlist', kwargs={'nivid': self.object.examen.niveau.nivid,'session':self.object.examen.session})

    def get_initial(self, **kwargs):
        initial=super(commposition_update, self).get_initial()
        initial=initial.copy()
        compid=self.kwargs['slug']
        compo=Composition.objects.get(compid=compid)
        examen=compo.examen
        
        
        if compo.comptype.id==1:
            initial['coefficient']=compo.ecue.ue.niveau.coefcm
        if compo.comptype.id==2:
            initial['coefficient']=compo.ecue.ue.niveau.coeftd
        if compo.comptype.id==3:
            
            initial['coefficient']=compo.ecue.ue.niveau.coeftp
        initial['ecue']=compo.ecue
        return initial

def addmanyano(request, compid):
    compo=Composition.objects.get(compid=compid)
    fano=compo.fano
    lano=compo.lano
    if compo.examen.afficher==False:
        if compo.ano==True:
            try: 
                for i in range(fano,lano+1):
                    try:
                        a=Anonymat.objects.create(ano=i, composition=compo)
                        a.save()
                    except:
                        pass
            except:
                pass
        else:
            return HttpResponse("Les notes de cette matières ne sont pas anonymaées")
       
    return HttpResponseRedirect(reverse('anolist',args=(compid,)))

class addoneano(CreateView):
    model=Anonymat
    form_class=oneanoform
    template_name="notes3/anonymat_create.html"
    def get_initial(self):
        initial = super(addoneano, self).get_initial()
        initial=initial.copy()
        compid=self.kwargs['compid']
        composition=Composition.objects.get(compid=compid)
        initial['composition']=composition
        max=Anonymat.objects.filter(composition=composition).aggregate(Max('ano'))
        initial['ano']=max['ano__max']+1
        return initial
    def get_success_url(self,  **kwargs):
        compid=self.kwargs['compid']
        return reverse_lazy('anolist', args=(compid,))
    def get_context_data(self,**kwargs):
        context=super(addoneano,self).get_context_data(**kwargs)
        compid=self.kwargs['compid']
        context['compid']=compid
        return context


def anonymat_list(request, compid):
    compo=Composition.objects.get(compid=compid)
    print(compo)
    ano=Anonymat.objects.filter(Q(composition=compo)).order_by('ano')
    return render(request,'notes3/anonymat_list.html',{'anolist':ano, 'compo':compo})

def anonymat_edit(request, compid):
    compo=Composition.objects.get(compid=compid)
    ano=Anonymat.objects.filter(Q(composition=compo) & Q(etudiant__isnull=True)).order_by('ano')
    return render(request,'notes3/anonymat_list.html',{'anolist':ano, 'compo':compo})

class anonymat_delete(DeleteView):
    model=Anonymat
    slug_field='ano'
  
    def delete(self, request, *args, **kwarg):
        self.object=self.get_object()
        note_ecue=Notes_ecue.objects.filter(anonymat__ano=self.object.ano)
        note_ecue.delete()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)
    def get_success_url(self,  **kwargs):
        return reverse_lazy('anolist', args=(self.object.composition.compid,))

class anonymat_update(UpdateView):
    model=Anonymat
    slug_field='ano'
    form_class=anoform
    template_name_suffix='update_form'

    def get_success_url(self, **kwargs):
        return reverse_lazy('eanolist', args=(self.object.composition.compid,))



def get_studentID(request):
    etudiant_id=request.GET.get("etudiant_id")
    composition=request.GET.get("composition_id")
    etud=Etudiant.objects.get(etudiantid=etudiant_id)
    context={}
    
    if etud:
        inscrip=Inscription.objects.filter(etudiant=etud)
        context['inscrip']=inscrip
        ue=compo.ecue.ue
        context['etudiant']=Inscription.objects.filter(niveau=ue.niveau)
        compo=Composition.objects.get(compid=composition)
        res_ue=Historic.objects.filter(Q(etudiant_id=etud) & Q(ue=ue) & Q(statut=1))
        if res_ue:
            context['resultat']='Admis'
        else:
            context['resultat']='Ajourné ou absent'
    else:
        context['inscrip']='Verifier le numéro'
        

    return render(request,'notes3/etudiant_id.html',context)

def listetudiant(request):
    id=request.GET.get("id_ano")
    if id==None:
        composition=request.GET.get("composition_id")
        composition=Composition.objects.get(compid=composition)
    else:
        ano=Anonymat.objects.get(ano=id)
        composition=ano.composition
    filtre=request.GET.get("filtre")
    datatype=request.GET.get("datatype")
    niv=composition.ecue.ue.niveau
    admis=Resultat_info.objects.get(id=1)
    dejaadmis=Notes_Ue.objects.filter(Q(resultat=admis) & Q(examen__ue=composition.ecue.ue)).values('etudiant')
    dejasaisi=Anonymat.objects.filter(Q(etudiant__isnull=False) & Q(composition=composition)).values('etudiant')
    if datatype=='anonymat':
        dejasaisi=Anonymat.objects.filter(Q(etudiant__isnull=False) & Q(composition=composition)).values('etudiant')
    if datatype=='note':
        dejasaisi=Notes_ecue.objects.filter(Q(etudiant__isnull=False) & Q(composition=composition)).values('etudiant')
    
    if filtre==None:
        list=Etudiant.objects.filter(etudiantid__in=Inscription.objects.filter(niveau=niv)
                                 .values('etudiant')).exclude(etudiantid__in=dejasaisi).order_by('nom','prenoms')
    else:
        list=Etudiant.objects.filter(Q(etudiantid__in=Inscription.objects.filter(niveau=niv)
                                 .values('etudiant')) & Q(nompren__startswith=filtre)).exclude(etudiantid__in=dejasaisi).order_by('nom','prenoms')
    listdef=list.exclude(etudiantid__in=dejaadmis)
    return render(request, 'notes3/inscritniveau.html',{'listes':listdef})



def etudiant_by_nce(request, nce):
    if request.GET.get("nce")==None:
        nce=''
    else:
        pass

    list=Etudiant.objects.filter(nce__contains=str(nce)).order_by('nompren')
    return render(request, 'notes3/inscritniveau.html',{'listes':list})

class compolist(ListView):
    model=Inscription
    template_name='notes3/composition_listing.html'
    def get_context_data(self, **kwargs):
        context=super(compolist,self).get_context_data(**kwargs)
        examid=self.kwargs['examid']
        examen=Examen.objects.get(id=examid)
        niveau=examen.niveau
        inscrit=Inscription.objects.filter(niveau=niveau).values('etudiant')
        validate=Notes_Ue.objects.filter(Q(examen__niveau=niveau) & Q(resultat__lt=3)).values('etudiant')
        exclu=Resultat.objects.filter(statut=4).values('etudiant')
        etlist=Etudiant.objects.filter(etudiantid__in=inscrit).exclude(Q(etudiantid__in=validate) & Q(etudiantid__in=exclu)).order_by('nom','prenoms')
        context['etlist']=etlist
        context['examen']=examen
        return context
def printComposition(request,id):
    buffer = io.BytesIO()
    response = HttpResponse(content_type = 'application/pdf')
    response['Content-Disposition'] = 'inline; filename = "deliberation.pdf"'
    doc = SimpleDocTemplate(buffer,   pagesizes = landscape(A4))
    doc.pagesize=landscape(A4)
    sp = ParagraphStyle('parrafos',   
              alignment = TA_CENTER,  
              fontSize = 16,  
              fontName = "Times-Roman",
              leading = 20)
    story = []
    examen=Examen.objects.get(id=id)
    niveau=examen.niveau
    inscrit=Inscription.objects.filter(niveau=niveau).values('etudiant')
    validate=Notes_Ue.objects.filter(Q(examen__niveau=niveau) & Q(resultat__lt=3)).values('etudiant')
    etlist=Etudiant.objects.filter(etudiantid__in=inscrit).exclude(etudiantid__in=validate).order_by('nom','prenoms')
    data=[]
    header=["Ordre","NCE","Nom","Prénoms","Date de naissance","Lieu de naissance"]
    data.append(header)
    j=1
    for et in etlist:
          line=[]
          line.append(j)
          line.append(et.nce)
          line.append(et.nom)
          line.append(et.prenoms)
          line.append(et.ddnais)
          line.append(et.lnais)
          data.append(line)
          j=j+1
        
    story=[]
    t=Table(data)
    spx = ParagraphStyle('parrafos',   
              alignment = TA_LEFT,  
              fontSize = 12,  
              fontName = "Times-Roman",  
              leading = 20)
    filp = Paragraph("<b> UFR Sciences de la nature </b>",  sp)
    story.append(filp)
    filp = Paragraph("<b> Listing de composiotion de la session "+str(examen.session)+ " de " +examen.ue.labels+ " ("+ examen.ue.code+") </b>",  sp)
    story.append(filp)
    niv = Paragraph("<b>"+examen.niveau.labels+"</b>",  sp)
    story.append(niv)
    filp = Paragraph("--------------------- ",  sp)
    story.append(filp)
    style = []
    style.append(('GRID',  (0,  0),  (-1,  -1),  0.5,  colors.black))
    t.setStyle(TableStyle(style))
    story.append(t)             
     
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def export_composition_to_excel(request, examid):
    response = HttpResponse(content_type='text/csv')
    examen=Examen.objects.get(id=examid)
    niveau=examen.niveau
    lauid=niveau.filiere.anuniv.lauid
    lanuniv=get_object_or_404(AnUniv,Q(auid=lauid))
    niveauanc=get_object_or_404(Niveau,Q(filiere__anuniv=lanuniv) & Q(code=niveau.code))
    ajour=Resultat_info.objects.get(id=3)
    anuniv=examen.anuniv
    if anuniv.inscrit==True:
        inscrit=Inscription.objects.filter(Q(niveau=niveau) & Q(inscrit=True)).distinct('etudiant').values_list('etudiant__etudiantid')
    else:
        inscrit=Inscription.objects.filter(Q(niveau=niveau) & Q(anuniv=anuniv)).distinct('etudiant').values_list('etudiant__etudiantid')
    ue=examen.ue
    ueanc=get_object_or_404(Ue,Q(niveau=niveauanc) & Q(code=ue.code))
    admis=Resultat_info.objects.get(id=1)
    cfc=Inscription.objects.filter(Q(cfc=True)).distinct('etudiant').values_list('etudiant__etudiantid')
    validate=Notes_Ue.objects.filter(Q(examen__niveau=niveauanc) & Q(resultat__id__lt=3) & Q(examen__ue=ueanc)).values_list('etudiant__etudiantid')
    ajourne=Notes_Ue.objects.filter(Q(examen__niveau=niveauanc) & Q(resultat__id=3) & Q(examen__ue=ueanc)).values_list('etudiant__etudiantid')
    exclu=Resultat.objects.filter(statut=4).exclude(etudiant_id__in=cfc).values_list('etudiant')
    
    if examen.session==1:
        filename=examen.niveau.code+examen.ue.code+str(examen.session)+".csv"
        response['Content-Disposition'] = 'attachment; filename="'+filename+'"'
        writer=csv.writer(response, delimiter=';')
        writer.writerow(["ORDRE","CFC","NCE","NOM","PRENOMS","DATE DE NAISSANCE","LIEU DE NAISSANCE"])
        etlist=Etudiant.objects.filter(etudiantid__in=inscrit).exclude(Q(etudiantid__in=validate) & Q(etudiantid__in=exclu)).order_by('nom','prenoms')
        j=1
        ettmp=etlist.exclude(etudiantid__in=validate)
        ettmp=ettmp
        listx=ettmp.exclude(etudiantid__in=exclu).order_by('nompren')
        for et in listx:
            if et.cfc==True:
                cfc='CFC'
            else:
                cfc='-'
            writer.writerow([j,cfc,et.nce,et.nom,et.prenoms,et.ddnais,et.lnais])
            j=j+1
        return response
    if examen.session==2:
        curau=get_object_or_404(AnUniv,Q(curau=True))
        etudcomp=Notes_ecue.objects.filter(Q(examen__anuniv=anuniv) & Q(examen__niveau=niveau)).values_list('etudiant')
        etudabst=Inscription.objects.filter(niveau=niveau).exclude(etudiant__in=etudcomp).values_list('etudiant__etudiantid')
        exam_ses1=get_object_or_404(Examen,Q(niveau=examen.niveau) & Q(ue=examen.ue) & Q(session=1) & Q(anuniv=curau))
        ajour=Notes_Ue.objects.filter(Q(examen__anuniv=curau) & Q(examen=exam_ses1) & Q(resultat=ajour)).values('etudiant')
        etinscr=Etudiant.objects.filter(etudiantid__in=ajour).exclude(etudiantid__in=validate)
        nbecue=UeInfo.objects.filter(ue=exam_ses1.ue).count()
        if nbecue>1 :
            if exam_ses1.ecue_ignored==True:
                compo_list=Composition.objects.filter(Q(examen=exam_ses1) & Q(comptype__id=1)|Q(comptype=3))
                for c in compo_list:
                    filename='/home/ufr-sn/Documents/listing/'+examen.niveau.code+c.ecue.code+c.comptype.labels+"_session_2.csv"
                    conserve=Notes_ecue.objects.filter(Q(composition=c) & Q(note__gte=10)).values_list('etudiant')
                    f=open(filename,'w')
                    writer=csv.writer(f, delimiter=';')
                    writer.writerow(["ORDRE","NCE","NOM","PRENOMS","DATE DE NAISSANCE","LIEU DE NAISSANCE"])
                    response['Content-Disposition'] = 'attachment; filename="'+filename+'"'
                    ettmp=etinscr.exclude(etudiantid__in=exclu)
                    list_cons=ettmp.exclude(etudiantid__in=conserve)
                    listx=list_cons.exclude(etudiantid__in=exclu).order_by('nompren')
                    j=1
                    for et in listx:
                        if et.cfc==True:
                            cfc='OUI'
                        else:
                            cfc='NON'
                        writer.writerow([j,et.cfc,et.nce,et.nom,et.prenoms,et.ddnais,et.lnais])
                        j=j+1
                    f.close()

            if exam_ses1.ecue_ignored==False:

                compo_list=Composition.objects.filter(Q(examen=exam_ses1) & Q(comptype__id=1))
                for c in compo_list:
                    filename='/home/ufr-sn/Documents/listing/'+examen.niveau.code+c.ecue.code+c.comptype.labels+"_session_2.csv"
                    response['Content-Disposition'] = 'attachment; filename="'+filename+'"'
                    f=open(filename,'w')
                    writer=csv.writer(f, delimiter=';')
                    writer.writerow(["ORDRE","NCE","NOM","PRENOMS","DATE DE NAISSANCE","LIEU DE NAISSANCE"])
                    conserve=Notes_ecue.objects.filter(Q(composition=c) & Q(note__gte=10)).values_list('etudiant')        
                    list_conserv=etinscr.exclude(etudiantid__in=conserve)
                    listx=list_conserv.exclude(etudiantid__in=exclu).order_by('nompren')
                    j=1
                    for et in listx:
                        writer.writerow([j,et.nce,et.nom,et.prenoms,et.ddnais,et.lnais])
                        j=j+1
                    f.close()

        if nbecue==1:
            filename='/home/ufr-sn/Documents/listing/'+examen.niveau.code+examen.ue.code+"_session_2.csv"
            response['Content-Disposition'] = 'attachment; filename="'+filename+'"'
            f=open(filename,'w')
            writer=csv.writer(f, delimiter=';')
            writer.writerow(["ORDRE","NCE","NOM","PRENOMS","DATE DE NAISSANCE","LIEU DE NAISSANCE"])
            ettmp=etinscr.exclude(etudiantid__in=exclu).order_by('nom','prenoms')
            listx=ettmp.exclude(etudiantid__in=exclu).order_by('nompren')
            if exam_ses1.ue.ueid==1127:
                xx=Notes_Ue.objects.filter(examen__ue__ueid=1128).values_list('etudiant')
                listx=listx.exclude(etudiantid__in=xx)
            if exam_ses1.ue.ueid==1128:
                xx=Notes_Ue.objects.filter(examen__ue__ueid=1127).values_list('etudiant')
                listx=listx.exclude(etudiantid__in=xx)
            j=1
            for et in listx:
                writer.writerow([j,et.nce,et.nom,et.prenoms,et.ddnais,et.lnais])
                j=j+1
            f.close()

    return HttpResponse('Fichier imprimé')



class composition_detail(DetailView):
    model=Composition
    template_name="notes3/composition_detail.html"
    slug_field='compid'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        dejasaisi=Anonymat.objects.filter(Q(composition=self.object) & Q(etudiant__isnull=False)).count()
        try:
            if self.object.ano==True:
                attendu=(self.object.lano-self.object.fano)+1
                pourcentage=round(100*dejasaisi/attendu,2)
                context['anonymats']=pourcentage
            if dejasaisi==0 and self.object.genano==True:
                get_random_list(self.object)
            else:
                print('test')
        except:
            pass
        noteds=Notes_ecue.objects.filter(Q(composition=self.object) & Q(etudiant__isnull=False)).count()
        context['notes']=noteds
        return context

class notes_ecue_create(CreateView):
    model=Notes_ecue
    form_class=notesform
    template_name="notes3/notes_ecue_create.html"
    def get_success_url(self, **kwargs):
        compid=self.kwargs['compid']
        return reverse_lazy('note_list', args=(compid,))
    def get_initial(self, **kwargs):
        initial=super(notes_ecue_create, self).get_initial()
        initial=initial.copy()
        initial['composition']=self.kwargs['compid']
        return initial
    def get_context_data(self, **kwargs):
        ctx = super(notes_ecue_create, self).get_context_data(**kwargs)
        ctx['compid']=self.kwargs['compid']
        composition=Composition.objects.get(compid=self.kwargs['compid'])
        ctx['composition']=composition
        return ctx

class notes_ecue_tdtp_create(CreateView):
    model=Notes_ecue
    form_class=tdtp_notesform
    template_name="notes3/notes_ecue_create.html"
    def get_success_url(self, **kwargs):
        compid=self.kwargs['compid']
        return reverse_lazy('note_list', args=(compid,))
    def get_initial(self, **kwargs):
        initial=super(notes_ecue_tdtp_create, self).get_initial()
        initial=initial.copy()
        compo=Composition.objects.get(compid=self.kwargs['compid'])
        initial['composition']=self.kwargs['compid']
        return initial
    def get_context_data(self, **kwargs):
        ctx = super(notes_ecue_tdtp_create, self).get_context_data(**kwargs)
        ctx['compid']=self.kwargs['compid']
        composition=Composition.objects.get(compid=self.kwargs['compid'])
        ctx['composition']=composition
        return ctx


class insertdata(CreateView):
    model=Notes_ecue
    form_class=tdtp_notesform
    template_name="notes3/notes_ecue_create.html"
    def get_success_url(self, **kwargs):
        compid=self.kwargs['composition']
        compo=Composition.objects.get(compid=compid)
        examid=compo.examen.id
        return reverse_lazy('examlist', args=(examid,compo.examen.session))
    def get_initial(self):
        initial= super().get_initial()
        initial=initial.copy()
        initial['etudiant']=self.kwargs['etudiantid']
        initial['composition']=self.kwargs['composition']
        ano=Anonymat.objects.filter(Q(composition__compid=self.kwargs['composition']) & Q(etudiant__etudiantid=self.kwargs['etudiantid']))
        compo=Composition.objects.get(compid=self.kwargs['composition'])
        if compo.ano==True:
            if ano.exists():
                initial['anonymat']=ano[0].ano
        return initial

class inserttdata(CreateView):
        model=Notes_ecue
        form_class=tdtp_notesform
        template_name="notes3/notes_ecue_create.html"
        def get_success_url(self, **kwargs):
            compid=self.kwargs['composition']
            compo=Composition.objects.get(compid=compid)
            examid=compo.examen.id
            return reverse_lazy('stats', args=(examid,))
        def get_initial(self):
            initial= super().get_initial()
            initial=initial.copy()
            initial['etudiant']=self.kwargs['etudiantid']
            initial['composition']=self.kwargs['composition']
            ano=Anonymat.objects.filter(Q(composition__compid=self.kwargs['composition']) & Q(etudiant__etudiantid=self.kwargs['etudiantid']))
            compo=Composition.objects.get(compid=self.kwargs['composition'])
            if compo.ano==True:
                if ano.exists():
                    initial['anonymat']=ano[0].ano
            return initial

        def get_context_data(self, **kwargs):
            context=super().get_context_data(**kwargs)
            compid=self.kwargs['composition']
            compos=Composition.objects.get(compid=compid)
            notes=Notes_ecue.objects.filter(composition=compos)
            context['compid']=compos.compid
            return context

class notes_ecues_delete(DeleteView):
    model=Notes_ecue
    slug_field='id'
    def get_success_url(self, **kwargs):
        compid=self.object.composition.compid
        return reverse_lazy('note_list', args=(compid,))

def clean_notes_ecue_admis(request,examid):
    examen=Examen.objects.get(id=examid)
    examen_list=Examen.objects.filter(ue=examen.ue).values('id')
    etudiant_deja_admis=Notes_Ue.objects.filter(Q(examen__in=examen_list) & Q(resultat__lt=3)).values('etudiant')
    note_ecue=Notes_ecue.objects.filter(Q(etudiant__in=etudiant_deja_admis) & Q(examen=examen))
    
    return HttpResponseRedirect(reverse('detexam', args=[examid,]))
    


class notes_ecues_list(ListView):
    model=Notes_ecue
    template_name="notes3/notes_ecues_list.html"
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs) 
        compid=self.kwargs['compid']
        compos=Composition.objects.get(compid=compid)
        notes=Notes_ecue.objects.filter(composition=compos).order_by('etudiant__nompren')
        nbre=Notes_ecue.objects.filter(composition=compos)
        context['compo']=compos
        context['notes']=notes
        context['nbre']=nbre.count()
        return context
class notes_ecue_update(UpdateView):
    model=Notes_ecue
    slug_field='id'
    template_name_suffix='_update_form'
    form_class=notesform
    def get_success_url(self, **kwargs):
        id=self.kwargs['slug']
        id_note=Notes_ecue.objects.get(id=id)
        etudiant=id_note.etudiant
        compid=id_note.composition.compid
        examid=id_note.composition.examen.id
        return reverse_lazy('get_ecue_result', args=(etudiant.etudiantid,examid,))
    def get_context_data(self, **kwargs):
        context=super(notes_ecue_update,self).get_context_data(**kwargs)
        id=self.kwargs['slug']
        note=Notes_ecue.objects.get(id=id)
        composition=note.composition
        context['composition']=composition
        return context
    def get_initial(self):
        initial= super(notes_ecue_update, self).get_initial()
        initial=initial.copy()
        noteid=self.kwargs['slug']
        note=Notes_ecue.objects.get(id=noteid)
        etudiant=note.etudiant
        composition=note.composition
        try:
            if composition.ano==True:
                try:
                    anonymat=get_object_or_404(Anonymat,Q(etudiant=etudiant) & Q(composition=composition))
                    initial['anonymat']=anonymat.ano
                except:
                    if composition.examen.session==2:
                        
                        try:
                            anuniv=get_object_or_404(AnUniv,Q(curau=True))
                            niveau=composition.examen.niveau
                            ue=composition.examen.ue
                            examen_ses1=get_object_or_404(Examen,Q(niveau=niveau) & Q(ue=ue) & Q(anuniv=anuniv) & Q(session=1))
                            resultat=get_object_or_404(Notes_Ue,Q(etudiant=etudiant) & Q(examen=examen_ses1))
                            if resultat.resultat.id==3:
                                compos_ses1=get_object_or_404(Composition,Q(examen=examen_ses1) & Q(ecue=composition.ecue) & Q(comptype=composition.comptype))        
                                
                                try:
                                    notes=get_object_or_404(Notes_ecue,Q(composition=compos_ses1) & Q(etudiant=etudiant))
                                    if notes.note>=10:
                                        initial['anonymat']=notes.anonymat
                                        initial['note']=notes.note


                                except:
                                    pass
                                

                        except:
                            pass
                    else:
                        pass
            else:
                initial['anonymat']=None
        except ObjectDoesNotExist:
            initial['anonymat']=None
        return initial

class tptd_notes_ecue_update(UpdateView):
    model=Notes_ecue
    slug_field='id'
    template_name_suffix='_update_form'
    form_class=tdtp_notesform
    def get_success_url(self, **kwargs):
        id=self.kwargs['slug']
        id_note=Notes_ecue.objects.get(id=id)
        compid=id_note.composition.compid
        examid=id_note.composition.examen.id
        return reverse_lazy('reclam_search', args=(examid,))
    def get_context_data(self, **kwargs):
        context=super(tptd_notes_ecue_update,self).get_context_data(**kwargs)
        id=self.kwargs['slug']
        note=Notes_ecue.objects.get(id=id)
        composition=note.composition
        context['composition']=composition
        return context
    
    
def openform_note(request,id):
      composition=Composition.objects.get(compid=id)
      examen=composition.examen.id
      context={
        'compid':id,
        'examid':examen,
        'filetype':2
      }
      return render(request,'notes3/upload_form.html',context)


def openform_ano(request, id):
      context={
        'compid':id,
        'filetype':1
      }
      return render(request,'notes3/upload_form.html',context)

def openfrom_tp_td(request,id):
    compo=Composition.objects.get(compid=id)
    t=tmpnote.objects.filter(composition=compo)
    context={
            'compid':id,
            'filetype':1
        }
    return render(request,'notes3/upload_tmp_form.html',context)


def upload_tmpnote(request,id):
    tx=tmpnote.objects.filter(composition__tsave=True)
    if tx.count()>0:
        text="Veuillez terminer de traiter "
        for t in tx:
            text=text+t.composition.ecue.labels+'\n'
        text=text+" avant de continuer"

        return HttpResponse(request,"Vou")
    t=tmpnote.objects.all()
    t.delete()
    if 'GET'==request.method:
        pass
    else:
            excel_file=request.FILES["excel_file"]
            data=get_data(excel_file)
            comp=Composition.objects.get(compid=id)
            prefix=comp.ecue.code+comp.comptype.code
            sheet=data[prefix]
            examen=comp.examen

            if examen.session==2:
                n=Notes_ecue.objects.filter(Q(composition=comp) & Q(examen=examen) & Q(reporter=False))
            else:
                n=Notes_ecue.objects.filter(Q(composition=comp) & Q(examen=examen))
            
            if n:
                n.delete()
            for row in sheet:
                if len(row)==0:
                            break
                if row[0]=='':
                    
                    tmp=tmpnote.objects.create(nompren=row[1], composition=comp,notes=row[2])
                    tmp.save()
                else:
                    try:
                        try:
                            if row[0][:4]=='CI02' or row[0][:4]=='Ci02':
                                    
                                    et=int(row[0][-8:])
                                    try: 
                                        etudiant=Etudiant.objects.get(etudiantid=et)
                                        admis=Resultat_info.objects.get(id=1)
                                        compense=Resultat_info.objects.get(id=2)
                                        res=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(resultat__id__lt=3) & Q(examen__ue=comp.ecue.ue)).count()
                                        print(etudiant,res)
                                        if res==0:
                                            tmp=tmpnote.objects.create(nompren=etudiant.nompren, composition=comp,notes=row[2],etudiant=etudiant)
                                            tmp.save()
                                        else:
                                            pass
                                    except ObjectDoesNotExist:
                                        etudiant=None
                                        tmp=tmpnote.objects.create(nompren=row[1], composition=comp,notes=row[2],etudiant=etudiant)
                                        tmp.save()
                                    
                        except:
                                e=Etudiant.objects.get(etudiantid=int(row[0]))
                                tmp=tmpnote.objects.create(nompren=row[1], composition=comp,notes=row[2],etudiant=e)
                                tmp.save()
                    except ObjectDoesNotExist:
                        tmp=tmpnote.objects.create(nompren=row[1], composition=comp,notes=row[2])
                        tmp.save()
                  
    if examen.session==2:
            report_notes(id)           
    t=tmpnote.objects.filter(composition=comp)
    context={}
    context["note"]=t
    return render(request, 'notes3/tmpnote.html', context)

def tmpnote_save(request,compid):
    comp=Composition.objects.get(compid=compid)
    comp.tsave=True
    comp.save()
    return render(request, 'notes3/tmpnote.html', context)
def checkInscription(etid,nivid):
    etudiant=Etudiant.objects.get(etudiantid=etid)
    niveau=Niveau.objects.get(nivid=nivid)
    Inscr=Inscription.objects.filter(Q(etudiant=etudiant) & Q(niveau=niveau))
    if Inscr:
        return True
    else:
        return False
def checkano(ano,compid):
    composition=Composition.objects.get(compid=compid)
    
    anox=Anonymat.objects.filter(Q(composition=composition) & Q(ano=ano))
    
    if anox:
        return True
    else: 
        return False

def uploadano(request,id,ft):
    if 'GET'==request.method:
            pass
    else:
            excel_file=request.FILES["excel_file"]
            data=get_data(excel_file)
            
            comp=Composition.objects.get(compid=id)
            
            if ft==1:
                if comp.ano==True and comp.comptype.id==1:
                        sheet = data["Cano"+comp.ecue.code]
                if comp.ano==True and comp.comptype.id==2:
                        sheet = data["Dano"+comp.ecue.code]
                if comp.ano==True and comp.comptype.id==7:
                        sheet = data["Xano"+comp.ecue.code]
                for row in sheet:
                        if len(row)==0:
                            break
                        try:
                            
                            a=Anonymat.objects.get(ano=int(row[1]))
                            try:
                                try:
                                    if row[0][:4]=='CI02' or row[0][:4]=='Ci02':
                                        et=int(row[0][-8:])
                                        try:
                                            etudiant=get_object_or_404(Etudiant,etudiantid=et)
                                            a.etudiant=etudiant
                                        except:
                                            if row[0][:8]=='CI020000':
                                                et=int(row[0][-8:])
                                                obj,created=Etudiant.objects.update_or_create(
                                                    etudiantid=et)
                                                etudiant=get_object_or_404(Etudiant,etudiantid=et)
                                                a.etudiant=etudiant 
                                except:
                                    et=row[0]
                                    etudiant=Etudiant.objects.get(etudiantid=et) 
                                    a.etudiant=etudiant
                                a.save()
                                et=None
                            except:
                                pass
                        except ObjectDoesNotExist:
                            return HttpResponse(str(row[1])+" n'existe pas")
                stat=Anonymat.objects.filter(composition=comp).aggregate(Max('ano'),Min('ano'))
                comp.fano=stat['ano__min']
                comp.lano=stat['ano__max']
                comp.save()
            if ft==2:
                if comp.comptype.id==1:
                    coefx=comp.ecue.ue.niveau.coefcm
                if comp.comptype.id==2:
                    coefx=comp.ecue.ue.niveau.coeftd
                if comp.comptype.id==3:
                    coefx=comp.ecue.ue.niveau.coeftp
                sess=comp.examen.session
           
                if comp.comptype.id==1:
                    sheet = data["Cnote"+comp.ecue.code]
                if comp.comptype.id==2:
                        sheet = data["Dnote"+comp.ecue.code]
                if comp.comptype.id==3:
                    sheet = data["Tnote"+comp.ecue.code]
                if comp.comptype.id==7:
                    sheet = data["Xnote"+comp.ecue.code]
                examen=comp.examen
                
                if examen.session==2:
                    if comp.ano==True:
                        n=Notes_ecue.objects.filter(Q(composition=comp) & Q(examen=examen) & Q(anonymat__gte=comp.fano) & Q(anonymat__lt=comp.lano) & Q(reclamation=False))
                    else:
                        n=Notes_ecue.objects.filter(Q(composition=comp) & Q(examen=examen) & Q(reporter=False) & Q(reclamation=False))
                else:
                    n=Notes_ecue.objects.filter(Q(composition=comp) & Q(examen=examen) & Q(reclamation=False))
             
                if n:
                    if comp.examen.afficher==False or comp.examen.afficher==None:
                        n.delete()
                    if comp.examen.afficher==True:
                        return HttpResponse('Les résultats de cette ue ont été déjà afficher. Traitez les reclamations')
                if examen.session==2:
                    n=Notes_ecue.objects.filter(Q(composition=comp) & Q(examen=examen) & Q(anonymat__isnull=True))
                    n.delete()
                for row in  sheet:
                    if len(row)==0:
                            break
                    if comp.ano==True:
                        try:
                            ano=Anonymat.objects.get(ano=row[0])
                            note=row[1]
                            
                            if checkano(row[0],id)==True:
                                n=Notes_ecue.objects.create(etudiant=ano.etudiant,composition=comp, 
                                    examen=examen,anonymat=ano, note=note,coef=coefx,ecue=comp.ecue,ue=comp.ecue.ue)
                                n.save()
                        except Exception as e:
                                print(str(e))
                           
                    if comp.ano==False:
                        etid=row[0]
                        print(etid)

                        try:

                            etudiant=Etudiant.objects.get(etudiantid=etid)
                            note=row[1]
                            obj,created=Notes_ecue.objects.update_or_create(
                                    etudiant=etudiant,
                                    composition=comp,
                                    examen=examen,
                                    defaults={'note':note,'coef':coefx,'ue':comp.ecue.ue,'ecue':comp.ecue}
                                    )
                        except ObjectDoesNotExist:
                            return HttpResponse(str(etid)+" n'existe pas")
                if examen.session==2:
                    report_notes(comp.compid)                           
                comp=Composition.objects.get(compid=id)
                exam_id=comp.examen.id                
                return HttpResponseRedirect(reverse('note_list', args=[comp.compid,]))
                
    return HttpResponse('Importation réussie')

def printlisting(request,examid):
    if request.method=="POST":
        form=formlisting(request.POST)
    else:
        form=formlisting()
    context={
        'form':form,
        'examid':examid
    }
    return render(request,'notes3/printlisting.html',context)





def view_deliberation(request,id):
        exam=Examen.objects.get(id=id)
        exam.finish=True
        exam.save()
        tp=Compotype.objects.get(id=3)
        cm=Compotype.objects.get(id=1)
        compcount=Composition.objects.filter(examen=exam).count()
        nbtp=Composition.objects.filter(Q(examen=exam) & Q(comptype=tp)).count()
        etudx=Notes_ecue.objects.filter(Q(reclamation=True) & Q(examen=exam)).distinct('etudiant').values('etudiant')
        if exam.afficher==False:
            note_etudiant=Notes_ecue.objects.values('etudiant').annotate(num_et=Count('etudiant')).filter(Q(examen=exam) & Q(num_et__lt=compcount)).order_by('etudiant__nompren','num_et')
        else:
            note_etudiant=Notes_ecue.objects.values('etudiant').annotate(num_et=Count('etudiant')).filter(Q(examen=exam) & Q(num_et__lt=compcount) & Q(etudiant__in=etudx)).order_by('etudiant__nompren','num_et')
        if note_etudiant:
            return HttpResponseRedirect(reverse('stats', args=[id,]))
        else:
            
            examen_list=Examen.objects.filter(ue=exam.ue).values('id')
            exam=Examen.objects.get(id=id)
            if exam.niveau.tp==False:
                composition=Composition.objects.filter(examen=exam).order_by('ecue__code')
            else:
                composition=Composition.objects.filter(examen=exam).order_by('ecue__code')
            etudiant=Notes_Ue.objects.filter(examen=exam).order_by("-moyenne")
            data=[]
            header=[]
            header.append('N°')
            for comp in composition:
                if comp.ano==True:
                    header.append("ano"+comp.ecue.code+comp.comptype.code)
                    header.append(comp.ecue.code+comp.comptype.code)
                else:
                    header.append(comp.ecue.code+comp.comptype.code)
            header.append('Moyenne')
            j=1
            for et in etudiant:
                line=[]
                line.append(j)
                for comp in composition:
                    dt=Notes_ecue.objects.filter(Q(examen=exam) & Q(composition=comp) & Q(etudiant=et.etudiant)).order_by('ecue__code')
                    if dt:
                        if comp.ano==True:
                            if dt[0].anonymat ==None:
                                line.append('')
                            else:
                                line.append(dt[0].anonymat.ano)
                            line.append(dt[0].note)    
                        else:
                            line.append(dt[0].note)
                line.append(et.moyenne)
                data.append(line)
                j=j+1
            context={}
            context['data']=data
            context['header']=header
            context['examen']=exam
            context['sup10']=Notes_Ue.objects.filter(Q(examen=exam) & Q(moyenne__gte=10)).count()
          
            return render(request,'notes3/deliberation.html',context)  
      
def checknote(request, examid):
    exam=Examen.objects.get(id=examid)
    compcount=Composition.objects.filter(examen=exam).count()
    admis=Resultat_info.objects.get(id=1)
    etudx=Notes_ecue.objects.filter(Q(reclamation=True) & Q(examen=exam)).distinct('etudiant').values('etudiant')
    if exam.afficher==False:
        note_etudiant=Notes_ecue.objects.values('etudiant').annotate(num_et=Count('etudiant')).filter(Q(examen=exam) & Q(num_et__lt=compcount)).order_by('composition__comptype','etudiant__nompren','num_et')
    else:
        note_etudiant=Notes_ecue.objects.values('etudiant').annotate(num_et=Count('etudiant')).filter(Q(examen=exam) & Q(num_et__lt=compcount) & Q(etudiant__in=etudx)).order_by('etudiant__nompren','num_et')
    context={}

    data=[]
   
    if note_etudiant:
        for row in note_etudiant:
            for comp in Composition.objects.filter(examen=exam).order_by('comptype'):
                list={}
                et=Notes_ecue.objects.filter(Q(etudiant=row['etudiant']) & Q(composition=comp))
                if et:
                    pass
                else:
                    etudiant=Etudiant.objects.get(etudiantid=row['etudiant'])
                    list={'etudiant': etudiant,'composition':comp}
                    data.append(list)
        context['stat']=data
        context['examid']=examid
        return render(request,'notes3/examen_erreur.html',context)
    else:
        return HttpResponseRedirect(reverse('etudiant_deja', args=[examid,]))



def printDeliberationPdf(request,id,psize):
    buffer = io.BytesIO()
    response = HttpResponse(content_type = 'application/pdf')
    height,width=A3
    exam=Examen.objects.get(id=id)
    filname='/délibératin' +'_'+exam.niveau.code+'_'+exam.ue.code+'_session_'+str(exam.session)+'.pdf'
    response['Content-Disposition'] = 'inline; filename = "'+filname+'"'
    if psize==1:

        doc = SimpleDocTemplate(buffer,   pagesizes = A4)
        doc.topMargin=1*cm
        doc.bottomMargin=1*cm
    if psize==2:
        doc = SimpleDocTemplate(buffer,   pagesizes = landscape(A4))
        doc.pagesize = landscape(A4)
        doc.topMargin=1*cm
        doc.bottomMargin=1*cm
    sp = ParagraphStyle('parrafos',   
              alignment = TA_CENTER,  
              fontSize = 16,  
              fontName = "Times-Roman",
              leading = 20)
    story = []
      
    composition=Composition.objects.filter(examen=exam).order_by('ecue__code')
    
    etudiant=Notes_Ue.objects.filter(examen=exam).order_by("-moyenne")
    data=[]
    header=[]
    header.append('N°')
    for comp in composition:
            if comp.ano==True:
                  header.append("a"+comp.ecue.code+comp.comptype.code)
                  header.append(comp.ecue.code+comp.comptype.code)
            else:
                  header.append(comp.ecue.code+comp.comptype.code)
    header.append('Moyenne')
    data.append(header)
    j=1
    styles = getSampleStyleSheet()
    for et in etudiant:
            line=[]
            line.append(j)
            for comp in composition:
                  dt=Notes_ecue.objects.filter(Q(examen=exam) & Q(composition=comp) & Q(etudiant=et.etudiant)).order_by('ecue__code')
                  if comp.ano==True:
                        if dt[0].anonymat==None:
                            line.append('')
                        else:
                            line.append(dt[0].anonymat.ano)
                        line.append(dt[0].note)    
                  else:
                      line.append(dt[0].note) 
            line.append(et.moyenne)
            data.append(line)
            j=j+1
    story=[]
    t=Table(data)
    spx = ParagraphStyle('parrafos',   
              alignment = TA_LEFT,  
              fontSize = 12,  
              fontName = "Times-Roman",  
              leading = 20)
    filp = Paragraph("<b> UFR Sciences de la nature </b>",  sp)
    story.append(filp)
    filp = Paragraph("<b> Listing de délibération </b>",  sp)
    story.append(filp)
    filp = Paragraph("---------------------",  sp)
    story.append(filp)
    niv = Paragraph("<b>"+exam.niveau.labels+"</b>",  sp)
    story.append(niv)
    filp = Paragraph("--------------------- ",  sp)
    story.append(filp)

    filp = Paragraph("--------------------- ",  sp)
    story.append(filp)
    comp = Paragraph("<b>"+comp.ecue.ue.labels+" ("+comp.ecue.ue.code+")</b>",  sp)
    story.append(comp)

    session = Paragraph("<b> Session: "+str(exam.session)+"</b>",  sp)
    story.append(session)
    filp = Paragraph("--------------------- ",  sp)
    story.append(filp)
    eff=Notes_Ue.objects.filter(examen=exam).count()
    effectif = Paragraph("<b> Effectif: "+str(eff)+"</b>", spx)
    story.append(effectif)
    moy10=Notes_Ue.objects.filter(Q(examen=exam) & Q(moyenne__gte=10)).count()
    pourc10=100*moy10/eff
    effectif = Paragraph("<b>Nombre de moyennes supérieures ou égales à 10: " + str(moy10) +" (" +str(round(pourc10,2)) + ") % </b>", spx)
    story.append(effectif)
    bardel = Paragraph("<b>Barre de déliberation: ___________/20 </b>", spx)
    story.append(bardel)
    bardel = Paragraph("<b>Nombre d'admis: ___________/" +str(eff) +"</b>", spx)
    story.append(bardel)
    spnb2 = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 10,  
              fontName = "Times-Roman",  
              leading = 10)
    spnb = ParagraphStyle('parrafos',   
              alignment = TA_LEFT,  
              fontSize = 12,  
              fontName = "Times-Roman",  
              leading = 75)
    filp = Paragraph("<b> *************************** </b>",  sp)
    story.append(filp)
    signature = Paragraph('<b>Vérifiez le calcul des moyennes avant de signer</b>',   spnb)
    story.append(signature)
    signature = Paragraph('<b>Date et signatures des responsables</b>',   spnb)
    story.append(signature)
    style = []
    style.append(('GRID',  (0,  0),  (-1,  -1),  0.5,  colors.black))
    filp = Paragraph("<b> *************************** </b>",  sp)
    story.append(filp)
    t.setStyle(TableStyle(style))
    style.append(('FONTSIZE', (0, 0), (-1, -1), 7),)
    story.append(t)
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    sujet='Listing de délibétation de '+exam.niveau.code
    message="Le listing de délibération de "+exam.niveau.code+ " de la session " + str(exam.session) + " de "+ exam.ue.code +" est disponible à l'ufr sn.\n"
    
    
    try:
          send_email_to(sujet,message,exam.niveau.nivid,id)
    except:
          pass
    return response

    

def view_resultat(request,id):
      exam=Examen.objects.get(id=id)
      composition=Composition.objects.filter(examen=exam).order_by('ecue__code')
      etudiant=Notes_Ue.objects.filter(examen=exam).order_by("-moyenne")
      data=[]
      header=["N°","NCE","Nom","Prenoms"]
      
      for comp in composition:
            if comp.ano==True:
                  header.append("ano"+comp.ecue.code+comp.comptype.code)
                  header.append(comp.ecue.code+comp.comptype.code)
            else:
                  header.append(comp.ecue.code+comp.comptype.code)
      header.append('Moyenne')
      header.append('Mention')
      j=1
      
      for et in etudiant:
            line=[]
            line.append(j)
            line.append(et.etudiant.nce)
            line.append(et.etudiant.nom)
            line.append(et.etudiant.prenoms)
            for comp in composition:
                dt=Notes_ecue.objects.filter(Q(examen=exam) & Q(composition=comp) & Q(etudiant=et.etudiant))
                if dt.exists:
                    if comp.ano==True:
                        if dt[0].anonymat==None:
                            line.append('')
                        else:
                            line.append(dt[0].anonymat.ano)
                        if dt[0].note<0:
                            line.append(0)
                        else:
                            line.append(dt[0].note)    
                    else:
                        if dt[0].note<0:
                            line.append(0)
                        else:
                            line.append(dt[0].note)
                else:
                    if comp.ano==True:
                        line.append('')
                        line.append('')
                    else:
                        line.append('')
            line.append(et.moyenne)
            line.append(get_mention(et.moyenne))
            data.append(line)
            j=j+1
      context={}
      context['data']=data
      context['header']=header
      context['examen']=exam
      return render(request,'notes3/view_resultat.html',context) 


def printResultatPdf(request,examid):
    buffer = io.BytesIO()
    response = HttpResponse(content_type = 'application/pdf')
    height,width=A4
    exam=Examen.objects.get(id=examid)
    filname='resultat' +exam.ue.code+'_session_'+str(exam.session)+'.pdf'
    response['Content-Disposition'] = 'inline; filename = "'+filname+'"'

    doc = SimpleDocTemplate(buffer,   pagesizes = landscape(A3))
    doc.pagesize = landscape(A3)
    exam=Examen.objects.get(id=examid)
    composition=Composition.objects.filter(examen=exam).order_by('ecue__code')
    etudiant=Notes_Ue.objects.filter(examen=exam).order_by("-moyenne")
    data=[]
    header=["N°","NCE","Nom","Prenoms"]
    colWidths = [1*cm,   3*cm,   3*cm,   7.5*cm]
    sp = ParagraphStyle('parrafos',   
              alignment = TA_CENTER,  
              fontSize = 16,  
              fontName = "Times-Roman",
              leading = 20)
    for comp in composition:
        
        if comp.ano==True:
            header.append("a"+comp.ecue.code+comp.comptype.code)
            colWidths.append(2.2*cm)
            header.append(comp.ecue.code+comp.comptype.code)
            colWidths.append(2.2*cm)
        else:
            header.append(comp.ecue.code+comp.comptype.code)
            colWidths.append(2*cm)
    header.append('Moy.')
    colWidths.append(2.2*cm)
    header.append('Ment.')
    colWidths.append(2.2*cm)
    data.append(header)
    j=1
    styles = getSampleStyleSheet()
    for et in etudiant:
        line=[]
        line.append(j)
        line.append(et.etudiant.nce)
        line.append(et.etudiant.nom)
        line.append(et.etudiant.prenoms)
        for comp in composition:
            dt=Notes_ecue.objects.filter(Q(examen=exam) & Q(composition=comp) & Q(etudiant=et.etudiant)).order_by('ecue__code')
            if comp.ano==True:
                if dt[0].anonymat==None:
                        line.append('')
                else:
                    line.append(dt[0].anonymat.ano) 
                    line.append(dt[0].note)      
            else:
                line.append(dt[0].note)
        if et.repeche==True:
            line.append(str(et.moyenne)+"*")
        else:
            line.append(et.moyenne)

        line.append(get_mention(et.moyenne))
        data.append(line)
        j=j+1
    story=[]
    t=Table(data,colWidths)
    filp = Paragraph("<b> UFR Sciences de la nature </b>",  sp)
    story.append(filp)
    filp = Paragraph("---------------------",  sp)
    story.append(filp)
    niv = Paragraph("<b>"+exam.niveau.labels+": "+exam.ue.labels+" ("+exam.ue.code+")</b>",  sp)
    story.append(niv)
    filp = Paragraph("--------------------- ",  sp)
    session = Paragraph("<b> Résultat session: "+str(exam.session)+"</b>",  sp)
    story.append(session)
    style = []
    style.append(('GRID',  (0,  0),  (-1,  -1),  0.5,  colors.black))
    filp = Paragraph("<b> *************************** </b>",  sp)
    story.append(filp)
    t.setStyle(TableStyle(style))
    story.append(t)
    spd = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 14,  
              fontName = "Times-Roman",  
              leading = 50)
    spn = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 14,  
              fontName = "Times-Roman")
    spnb1 = ParagraphStyle('parrafos',   
              fontSize = 10,  
              fontName = "Times-Roman")
    spnb2 = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 10,  
              fontName = "Times-Roman",  
              leading = 10)
    filp = Paragraph("<b>---------------------</b>",  spnb1)
    story.append(filp)
    nb = Paragraph("<b>NB: Vous disposez trois jours pour entamer une procédure de reclamation à compter de la date de signature de ces résultats</b>",   spnb2)
    story.append(nb)
    nb = Paragraph("<b>NB: Une moyenne accompgnées d'une astérix (*) signifie que l'étudiant(e) a été repêché(e) </b>",   spnb2)
    story.append(nb)
    ledoyen = Paragraph('<b>Le doyen</b>',   spd)
    story.append(ledoyen)
    nomdoyen = Paragraph('<b>TIHO Séydou</b>',   spn) 
    story.append(nomdoyen)
     
   
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
class salle_list(ListView):
    model=Salle
    template_name='notes3/salle_list.html'
    context_object_name='salles'
    
class salle_create(CreateView):
    model=Salle
    form_class=salleform
    template_name='notes3/salle_create.html'
    def get_success_url(self):
        return reverse_lazy( 'salles')

class salle_update(UpdateView):
    model=Salle
    template_suffix_name='_update_form'
    slug_field='id'
    fields=['nom','place','utiliser']
    template_name_suffix='_update_form'
    def get_success_url(self):
        return reverse_lazy( 'salles')

class enseignant_list(ListView):
    model=Enseignant
    template_name='notes3/enseignant_list.html'
    context_object_name='enseignants'



class enseignant_create(CreateView):
    model=Enseignant
    form_class=enseigform
    template_name='notes3/enseignant_create.html'
    def get_success_url(self):
        return reverse_lazy( 'enseignant')

class enseignant_update(UpdateView):
    model=Enseignant
    template_suffix_name='_update_form'
    slug_field='id'
    fields=['emploi','nompren','emails','contact']
    template_name_suffix='_update_form'
    def get_success_url(self):
        return reverse_lazy( 'enseignant')
class horaire_create(CreateView):
    model=Heures
    form_class=horaireform
    template_name='notes3/horaire_create.html'
    def get_initial(self):
        enseigid=self.kwargs['enseigid']
        initial= super(horaire_create, self).get_initial()
        initial=initial.copy()
        initial['enseignant']=Enseignant.objects.get(id=enseigid)
        return initial

class resultat_list(ListView):
    model=Resultat
    template_name='notes3/resultat_list.html'
    def get_context_data(self, **kwargs):
        context=super(resultat_list, self).get_context_data(**kwargs)
        etudiant_id=self.kwargs['etudiant_id']
        try:
            etudiant=get_object_or_404(Etudiant,Q(etudiantid=etudiant_id))
            resultat=Resultat.objects.filter(etudiant=etudiant).order_by('niveau')
            context['resultats']=resultat
            context['etudiant']=etudiant
            curau=get_object_or_404(AnUniv,Q(curau=True))
            context['curau']=curau.auid
            context['absent']=False
        except:
            etudiant=get_object_or_404(Etudiant,Q(etudiantid=etudiant_id))
            context['etudiant']=etudiant
            context['absent']=True
            curau=get_object_or_404(AnUniv,Q(curau=True))
            context['curau']=curau.auid
        
        return context

class etudiant_list(ListView):
    model=Etudiant
    template_name='notes3/etudiant_list.html'
    def get_context_data(self, **kwargs):
        context= super(etudiant_list, self).get_context_data(**kwargs)
        if self.request.GET.get('etudiantid'):

            etudiant=Etudiant.objects.get(etudiantid=self.request.GET.get('etudiantid'))
            context['etudiant']=etudiant
        else:
            letudiant=Etudiant.objects.filter(etudiantid__in=Inscription.objects.all().values('etudiant'))
            paginator=Paginator(letudiant,100)
            page=self.request.GET.get('page')
            etudiants=paginator.get_page(page)
            context['etudiants']=etudiants

        return context
  

def maj(request):
    cursor=connection.cursor()
    cursor.execute("select maj()")
    return reverse_lazy('filieres')

@login_required
def Releve(request, etudiantid, niveauid):
    etudiant=Etudiant.objects.get(etudiantid=etudiantid)
    semestre_resultat_etudiant(niveauid,etudiantid)
    notes=Notes_Ue.objects.filter(Q(etudiant__etudiantid=etudiantid) & Q(examen__niveau__nivid=niveauid)).order_by('examen__ue__semestre','examen__ue__biguecat__categorie','examen__ue__code')
    context={}
    niveau=Niveau.objects.get(nivid=niveauid)
    context['notes']=notes
    context['etudiant']=etudiant
    context['niveauid']=niveauid
    resultat=get_object_or_404(Resultat,Q(etudiant=etudiant) & Q(niveau=niveau))
    context['resultat']=resultat
    curau=get_object_or_404(AnUniv,Q(curau=True))
    context['curau']=curau.auid
    update_res_releve(niveauid,etudiantid)
    return render(request, 'notes3/releve.html',context)


class create_notes_ue(CreateView):
    model=Notes_Ue
    form_class=addnote
    template_name='notes3/notes_ue_create.html'
    def get_context_data(self, **kwargs):
        context=super(create_notes_ue, self).get_context_data(**kwargs)
        etudiant_id=self.kwargs['etudiantid']
        niveau_id=self.kwargs['nivid']
        etudiant=Etudiant.objects.get(etudiantid=etudiant_id)
        context['etudiant']=etudiant
        context['niveauid']=niveau_id
        return context
    def get_initial(self):
        etudiant_id=self.kwargs['etudiantid']
        initial= super(create_notes_ue, self).get_initial()
        initial=initial.copy()
        initial['etudiant']=etudiant_id
        return initial
    def get_success_url(self):
        etudiant_id=self.kwargs['etudiantid']
        nivid=self.kwargs['nivid']
        return reverse_lazy('releve', args=(etudiant_id,nivid))
import decimal

def printReleve(request, etudiantid, niveauid):
    niveau=Niveau.objects.get(nivid=niveauid)
    etudiant=Etudiant.objects.get(etudiantid=etudiantid)
    semestre_resultat_etudiant(niveauid,etudiantid)
    bigcat_resultat_etudiant(etudiantid,niveauid)
    semestre=Ue.objects.filter(niveau=niveau).distinct('semestre').order_by('semestre').values('semestre') 
    buffer = io.BytesIO()
    response = HttpResponse(content_type = 'application/pdf')
    response['Content-Disposition'] = 'inline; filename = "'+etudiant.nce+'_'+niveau.code+'.pdf"'
    doc = SimpleDocTemplate(buffer,   pagesizes = A4)
    story = []
    styles = getSampleStyleSheet()
    admis=Statut_info.objects.get(id=1)
    cond=Statut_info.objects.get(id=2)
    aj=Resultat_info.objects.get(id=3)
    curau=get_object_or_404(AnUniv, curau=True)
    spnb1 = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 8,  
              fontName = "Times-Roman")
    splab = ParagraphStyle('parrafos',   
              alignment = TA_LEFT,  
              fontSize = 8,  
              fontName = "Times-Roman")
    res_etud=get_object_or_404(Resultat,  Q(niveau=niveau) & Q(etudiant=etudiant))
    
    data=[]
    theader = ['Semestre',   'Catégorie',   'Intitulés',   'Notes',   'Crédits',   'Validées',   'Moy.',   'Mention']
    data.append(theader)
    for sem in semestre:
        uecats=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(examen__ue__semestre=sem['semestre'])).values('examen__ue__biguecat').distinct('examen__ue__biguecat').order_by('examen__ue__biguecat')
        for uec in uecats:
            if res_etud.statut==admis:
                notes=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(examen__ue__semestre=sem['semestre']) & Q(examen__ue__biguecat=uec['examen__ue__biguecat']) & Q(resultat__lt=3))
            else:
                tmp=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(examen__ue__semestre=sem['semestre']) & Q(examen__ue__biguecat=uec['examen__ue__biguecat']))
                ajour_sess1=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(examen__ue__semestre=sem['semestre']) & Q(examen__ue__biguecat=uec['examen__ue__biguecat']) & Q(examen__session=1) & Q(resultat=aj)).values('id')
                notes=tmp.exclude(id__in=ajour_sess1)
            line=[]
            nl=0
            moy_uec=Resultat_bigcat.objects.filter(Q(etudiant=etudiant) & Q(niveau=niveau) & Q(semestre=sem['semestre']) & Q(biguecat=uec['examen__ue__biguecat'])).values('moyenne')
            
            for note in notes:
                s=translate_sem(note.examen.ue.semestre)
                if nl==0:
                    line.append(s)
                else:
                    line.append('')
                if nl==0:
                    line.append(Paragraph(note.examen.ue.biguecat.categorie,splab))
                else:
                    line.append('')
                line.append(Paragraph(note.examen.ue.labels,splab))
                if note.resultat.id==1:
                    line.append(note.moyenne)
                if note.resultat.id==2:
                    text=str(note.moyenne)+'*'
                    line.append(text)
                if note.resultat==aj:
                    line.append(note.moyenne)
                line.append(note.examen.ue.credits)
                line.append(note.examen.anuniv.labels)
                if nl==0:
                    if moy_uec[0]['moyenne']>=10:
                        line.append(moy_uec[0]['moyenne'])
                    else:
                        line.append("Ajourné")
                else:
                    line.append('')
                if nl==0:
                    line.append(get_mention(moy_uec[0]['moyenne']))
                else:
                    line.append('')
                data.append(line)
                line=[]
                nl=nl+1
      
        moy_sem=Resultat_semestre.objects.filter(Q(etudiant=etudiant) & Q(niveau=niveau) & Q(semestre=sem['semestre'])).values('moyenne')
        
        data.append(['Moyenne du semestre '+str(sem['semestre']),'','','','','',moy_sem[0]['moyenne'],get_mention(moy_sem[0]['moyenne'])])
    moy_an=Resultat.objects.filter(Q(etudiant=etudiant) & Q(niveau=niveau)).values('moyenne')
    data.append(['Moyenne annuelle ','','','','','',round(moy_an[0]['moyenne'],2),get_mention(moy_an[0]['moyenne'])])   
    spx = ParagraphStyle('parrafos',   
              alignment = TA_CENTER,  
              fontSize = 14,  
              fontName = "Times-Roman",  
              leading = 50)
    spx2 = ParagraphStyle('parrafos',   
              alignment = TA_CENTER,  
              fontSize = 14,  
              fontName = "Times-Roman",  
              leading = 20)

    sp = ParagraphStyle('parrafos',   
              alignment = TA_LEFT,  
              fontSize = 10,  
              fontName = "Times-Roman",
              leading = 20)
    x=Paragraph('.',spx)
    story.append(x)
    header = Paragraph("<b>Relevé de notes provisoire</b>",   spx2)
    story.append(header)
    fil = Filiere.objects.get(niveau = niveau)
    filp = Paragraph("<b>"+fil.specialite+"</b>",  spx2)
    story.append(filp)
    niv = Paragraph("<b>"+niveau.labels+"</b>",  spx2)
    story.append(niv)
    nce = Paragraph("Numéro de carte d'étudiant: <b>"+etudiant.nce+"</b>",  sp )
    story.append(nce)
    nompren = Paragraph("Nom et prénoms: <b>"+etudiant.nom+" "+etudiant.prenoms+"</b>",   sp)
    story.append(nompren)
    dl = Paragraph("Date et lieu de naissance: <b>"+str(etudiant.ddnais.strftime("%d/%m/%y"))+"</b> à <b>"+etudiant.lnais+"</b>",   sp)
    story.append(dl)
    res=Resultat.objects.filter(Q(etudiant=etudiant) & Q(niveau=niveau)).values('nban')
    if res[0]['nban'] == 1:
        rdbl = Paragraph("Redoublant: <b>NON</b>",   sp)
    else:
        rdbl = Paragraph("Redoublant: <b>OUI</b>",   sp)
    story.append(rdbl)
    t = Table(data,   colWidths = [1.5*cm,   3.1*cm,   7.5*cm,   1.5*cm,   1.3*cm,   2*cm,   1.2*cm,  1.7*cm])
    if res_etud.statut==admis:
        stat=Notes_Ue.objects.values('examen__ue__semestre').annotate(nb=Count('examen__ue'))\
            .filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(resultat__lt=3))
        print(stat)
    else:
        stat=Notes_Ue.objects.values('examen__ue__semestre').annotate(nb=Count(Case(When(resultat__lt=3,then=1),When(Q(examen__session=2) & Q(resultat=aj),then=1))))\
            .filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau))
        print(stat)
    
    style=[]
    style.append(('GRID',  (0,  0),  (-1,  -1),  0.5,  colors.black))
    style.append(('FONTSIZE',   (0,   0),   (-1,   -1),   8))
    style.append(('VALIGN',   (0,   0),   (-1,   -1),   'MIDDLE'))
    style.append(('SPAN',   (0,    1),   (0,   stat[0]['nb']),))
    style.append(('SPAN',   (0,    stat[0]['nb']+2),   (0,   stat[0]['nb']+stat[1]['nb']+1),))
    style.append(('SPAN',   (0,    stat[0]['nb']+1),   (5,   stat[0]['nb']+1),))
    style.append(('SPAN',   (0,    stat[0]['nb']+stat[1]['nb']+2),   (5,   stat[0]['nb']+stat[1]['nb']+2),))
    style.append(('SPAN',   (0,    stat[0]['nb']+stat[1]['nb']+3),   (5,   stat[0]['nb']+stat[1]['nb']+3),))
    sem=Notes_Ue.objects.values('examen__ue__semestre').annotate(nb=Count('examen__ue'))\
        .filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(resultat__lt=3))
    col=[1,6,7]
    for c in  col:
        srow=1
        erow=0   
        for s in sem:
            if res_etud.statut==admis:
                ustat=Notes_Ue.objects.values('examen__ue__biguecat').annotate(nb=Count('examen__ue'))\
                    .filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(resultat__lt=3) & Q(examen__ue__semestre=s['examen__ue__semestre'])).order_by('examen__ue__biguecat')
            else:
                ustat=Notes_Ue.objects.values('examen__ue__biguecat').annotate(nb=Count(Case(When(resultat__lt=3,then=1),When(Q(examen__session=2) & Q(resultat=aj),then=1))))\
                    .filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau)  & Q(examen__ue__semestre=s['examen__ue__semestre'])).order_by('examen__ue__biguecat')


            
            for u in ustat:
                if u['nb']==1:
                    srow=srow+u['nb']
                if u['nb']>1:
                    erow=srow+u['nb']-1
                    style.append(('SPAN',   (c,    srow),   (c,   erow),))
                    srow=erow+1
            srow=srow+1
    
   
    t.setStyle(TableStyle(style))
    story.append(t)
    spd = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 12,  
              fontName = "Times-Roman",  
              leading = 40)
    spn = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 12,  
              fontName = "Times-Roman")
    spnb1 = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 8,  
              fontName = "Times-Roman")
    spnb2 = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 8,  
              fontName = "Times-Roman",  
              leading = 10)
    spass = ParagraphStyle('parrafos',   
              alignment = TA_LEFT,  
              fontSize = 10,  
              fontName = "Times-Roman",  
              leading = 10)
    nb = Paragraph("Les moyennes accompagnées de * ont été compensées",   spnb1)
    story.append(nb)
    nb = Paragraph("Valable 3 mois à compter de sa date de signature",   spnb2)
    story.append(nb)
    if niveau.nivto==None:
        pass
    else:
        if res_etud.statut==admis:
            nb = Paragraph("Admis(e) en <b>"+niveau.nivto+"</b>",   spass)
        if res_etud.statut==cond:
            nb = Paragraph("Admis(e) en <b>"+niveau.nivto+" conditionnelle </b>",   spass)
            
    story.append(nb)
    ledoyen = Paragraph('<b>Le Directeur</b>',   spd)
    story.append(ledoyen)
    nomdoyen = Paragraph('<b>TIHO Séydou</b>',   spn) 
    story.append(nomdoyen)
    doc.build(story)    
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def translate_sem(semestre):
    if semestre==1:
        sem="Un"
    if semestre==2:
        sem="Deux"
    if semestre==3:
        sem="Trois"
    if semestre==4:
        sem="Quatre"
    if semestre==5:
        sem="Cinq"
    if semestre==6:
        sem="Six"

    return sem

def get_mention(moy):
  mention = ''
  if moy < decimal.Decimal(10):
    mention = 'Ajourné'
  if moy >= decimal.Decimal(10) and moy < decimal.Decimal(12):
    mention = 'Passable'
  elif moy >= decimal.Decimal(12) and moy < decimal.Decimal(14):
    mention = 'Assez-bien'
  elif moy >= decimal.Decimal(14) and moy < decimal.Decimal(16):
    mention = 'Bien'
  elif moy >= decimal.Decimal(16) and moy < decimal.Decimal(18):
    mention = 'Très bien'
  elif moy >= decimal.Decimal(18) and moy <= decimal.Decimal(20):
    mention = 'Excéllent'
  return mention


def studsearch_form(request):
    
    if request.method=='POST':
        form=etudiantForm(request.POST)
        if form.is_valid():
            etudiantid=form.cleaned_data['etudiantid']
            return HttpResponseRedirect(reverse('resultats', args=[etudiantid,]))
    else:
        form=etudiantForm()
    curau=get_object_or_404(AnUniv,Q(curau=True))
    return render(request, 'notes3/etudiant_search.html',{'form':form,'curau':curau.auid})


def reclam_sform(request,examid):
    if request.method=='POST':
        form=etudiantForm(request.POST)
        if form.is_valid():
            etudiantid=form.cleaned_data['etudiantid']
           
            return HttpResponseRedirect(reverse('get_ecue_result', args=[etudiantid,examid]))
    else:
        form=etudiantForm()
        
    return render(request, 'notes3/etudiant_search.html',{'form':form,'examid':examid})



def infonotes(request,etudiantid,examid):
    examen=Examen.objects.get(id=examid)
    resultat=Notes_Ue.objects.filter(Q(examen__ue=examen.ue) & Q(etudiant__etudiantid=etudiantid))
    try:

        etudiant=Etudiant.objects.get(etudiantid=etudiantid)
    except ObjectDoesNotExist:
        return HttpResponse("Cet etudiant n'existe pas")
    notes=Notes_ecue.objects.filter(Q(examen=examen) & Q(etudiant=etudiant))
    context={}
    context['notes']=notes
    context['etudiant']=etudiant
    context['examen']=examen
    compolist=Composition.objects.filter(examen=examen)
    context['composition']=compolist
    context['resultat']=resultat
    context['examen']=examen
    return render(request,'notes3/notes_info.html',context)

def report_notes_etudiant(etudiantid,examid):
    examen=Examen.objects.get(id=examid)
    exam_ses1=get_object_or_404(Examen,Q(niveau=examen.niveau) & Q(ue=examn.ue) & Q(session=1) & Q(anuniv=examen.anuniv))
    compos=Composition.objects.filter(examen=exam_ses1)
    
        


class get_ue_list(ListView):
    model=Ue
    template_name='notes3/uelist.html'
    def get_context_data(self,**kwargs):
        context=super(get_ue_list, self).get_context_data(**kwargs)
        nivid=self.kwargs['niveauid']
        ues=Ue.objects.filter(niveau__nivid=nivid).order_by('semestre','code')
        credit=Ue.objects.filter(Q(niveau__nivid=nivid) & Q(inuse=True)).aggregate(credit=Sum('credits'))
        uecount=Ue.objects.filter(Q(niveau__nivid=nivid)).count()
        niveau=Niveau.objects.get(nivid=nivid)
        context['ues']=ues
        context['niveau']=nivid
        context['credits']=credit['credit']
        auid=get_object_or_404(AnUniv,Q(curau=True))
        context['curau']=niveau.filiere.anuniv.auid
        context['uecount']=uecount

        return context

class get_ecue_list(ListView):
    model=UeInfo
    template_name='notes3/ecuelist.html'
    def get_context_data(self, **kwargs):
        context=super(get_ecue_list,self).get_context_data(**kwargs)
        ueid=self.kwargs['ueid']
        ue=Ue.objects.get(ueid=ueid)
        ecue=UeInfo.objects.filter(ue__ueid=ueid).order_by('labels')
        context['ecues']=ecue
        context['niveau']=ue.niveau.nivid
        context['ueid']=ueid
        return context



def ecuesearch_form(request):
    if request.method=='POST':
        form=ecueform(request.POST)
        if form.is_valid():
            nom=form.cleaned_data['labels']
            return HttpResponseRedirect(reverse('ecues_res', args=[nom,]))
    else:
        form=ecueform()
            
    return render(request, 'notes3/ueinfolist.html',{'form':form})

def ecueslist(request,labels):
    ueinfo=UeInfo.objects.filter(labels__icontains=labels).order_by('niveau','labels')
    context={}
    context['ueinfos']=ueinfo
    return render(request,'notes3/ueinfolist.html',context)

    
    
class etudiant_update(UpdateView):
    model=Etudiant
    template_name_suffix='_update_form'
    fields=['nom','prenoms','ddnais','lnais','epss','cfc']
    slug_field='etudiantid'

    def get_success_url(self):
        etid=self.kwargs['slug']
        return reverse_lazy('resultats', args=(etid,))

class notes_ue_update(UpdateView):
    model=Notes_Ue
    template_name_suffix='_update_form'
    form_class=upnote
    slug_field='id'
    def get_success_url(self):
        id=self.kwargs['slug']
        note=Notes_Ue.objects.get(id=id)
        etudiantid=note.etudiant.etudiantid
        nivid=note.examen.niveau.nivid
        return reverse_lazy('releve', args=(etudiantid,nivid))
    def get_initial(self):
        initial=super(notes_ue_update, self).get_initial()
        initial=initial.copy()
        id=self.kwargs['slug']
        note=Notes_Ue.objects.get(id=id)
        initial['examen']=note.examen.id
        return initial
    
def create_examen_ue_niveau_list(request):
    examid=request.GET.get("examid")
    examen=Examen.objects.get(id=examid)
    examen_list=Examen.objects.filter(Q(niveau=examen.niveau) & Q(ue=examen.ue))
    
    context={}
    context['examens']=examen_list
    return render(request, 'notes3/tmp_examen_list.html' ,context)

class deliberation_update(UpdateView):
    model=Examen
    template_name_suffix='_update_delib'
    fields=['delib_cm', 'delibdate']
    slug_field='id'
    def get_success_url(self):
        examid=self.kwargs['slug']
        return reverse_lazy('prttest', args=(examid,))
    





def set_result(request,examid):
    examen=Examen.objects.get(id=examid)
    admis=Resultat_info.objects.get(id=1)
    Notes_Ue.objects.filter(Q(examen__id=examid) & Q(moyenne__gte=examen.delib_cm)).update(resultat=admis)
    ajourne=Resultat_info.objects.get(id=3)
    Notes_Ue.objects.filter(Q(examen__id=examid) & Q(moyenne__lt=examen.delib_cm)).update(resultat=ajourne)
    meta10(examid)

    return reverse_lazy('resprinter', args=(examid,))

def meta10(examid):
    admis=Resultat_info.objects.get(id=1)
    a10=Notes_Ue.objects.filter(Q(resultat=admis) & Q(moyenne__lt=10) & Q(examen__id=examid)).values('etudiant')
    
    ecue_to_change=Notes_ecue.objects.filter(Q(etudiant__in=a10) & Q(examen__id=examid)).annotate(mn=Min('note')).values('etudiant','composition','mn')
    for e in ecue_to_change:
        print(e)


def ue_resultat(request, examid):
    compositions=Composition.objects.filter(examen__id=examid)
    examen=Examen.objects.get(id=examid)
    admis=Resultat_info.objects.get(id=1)
    ajourne=Resultat_info.objects.get(id=3)
    
    etudiants=Notes_Ue.objects.filter(examen=examen).order_by('-moyenne')
    data=[]
    header=['NCE','Nom','Prenoms','Date de naissance']
    for compo in compositions:
        if compo.ano==True:
            header.append("ano_"+compo.ecue.code)
            header.append(compo.ecue.code)
        else:
            header.append(compo.ecue.code)
    header.append('moyenne')
    header.append('Resultat')
    for etud in etudiants:
        line=[]
        line.append(etud.etudiant.nce)
        line.append(etud.etudiant.nom)
        line.append(etud.etudiant.prenoms)
        line.append(etud.etudiant.ddnais)
        note_et=Notes_ecue.objects.filter(Q(etudiant=etud.etudiant) & Q(composition__examen=examen)).order_by('composition')
        for note in note_et:
            if note.anonymat==None:
                pass
            else:
                line.append(note.anonymat.ano)
            line.append(note.note)
        resmoy=Notes_Ue.objects.filter(Q(etudiant=etud.etudiant) & Q(examen=examen))
        line.append(resmoy[0].moyenne)
        line.append(resmoy[0].resultat)
        data.append(line)
    context={}
    context["header"]=header
    context["data"]=data
    context["examen"]=Examen.objects.get(id=examid)
    return render (request, 'notes3/listing_resultat.html',context)


def delmanyano(request, compid):
    a=Anonymat.objects.filter(Q(etudiant__isnull=True) & Q(composition__id=compid))
    if a:
        a.delete()
    return reverse_lazy('anolist') 
    


class new_student(CreateView):
    model=Etudiant
    template_name='notes3/etudiant_create.html'
    success_url=reverse_lazy('student_search')
    form_class=CetudiantForm

def viewStudentDetail(request,examid,etudiantid):
    note_etud=Notes_ecue.objects.filter(Q(etudiant__etudiantid=etudiantid) & Q(examen__id=examid))
    compolist=Composition.objects.filter(examen__id=examid)
    data=[]
    examen=Examen.objects.get(id=examid)
    etudiant=Etudiant.objects.get(etudiantid=etudiantid)
    notes=Notes_ecue.objects.filter(Q(composition__in=compolist) & Q(etudiant__etudiantid=etudiantid))
    context={}
    res=Resultat.objects.filter(Q(etudiant=etudiant))
    histo=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__niveau__code=examen.niveau.code) & Q(examen__ue__code=examen.ue.code))
    context['notes']=notes
    context['res']=res
    context['histo']=histo
    return render(request, 'notes3/etudiant_notes_detail.html',context)

class updatenote(UpdateView):
    model=Notes_ecue
    fields=['note','anonymat']
    template_name_suffix='update_note3'
    slug_field=id

def clean_notes_ecue(request,examid):
    exam=Examen.objects.get(id=examid)
    compos=Composition.objects.filter(examen=exam)
    compcount=Composition.objects.filter(examen=exam).count()
    note_etudiant=Notes_ecue.objects.values_list('etudiant').annotate(num_et=Count('etudiant')).filter(Q(examen=exam) & Q(num_et__lt=compcount)).order_by('etudiant__nompren','num_et')
    for etudiant in note_etudiant:
        
        for compo in compos:
            note=Notes_ecue.objects.filter(Q(composition=compo) & Q(etudiant__etudiantid=etudiant[0]))
            if note.exists():
                pass
            else:
                etud=Etudiant.objects.get(etudiantid=etudiant[0])
                n=Notes_ecue.objects.create(composition=compo, etudiant=etud, note=0)
                n.save()
    return HttpResponseRedirect(reverse('etudiant_deja', args=[examid,]))


def list_tmp_etudiant(request):
    id=request.GET.get("compid")
    print(id)
    comp=Composition.objects.get(compid=id)
    print(comp)
    inscr=Inscription.objects.filter(niveau=comp.examen.niveau).values("etudiant")
    filtre=request.GET.get("filtre")
    dejasaisi=tmpnote.objects.filter(etudiant__isnull=False).values('etudiant')
    if filtre==None:
        listet=Etudiant.objects.filter(etudiantid__in=inscr).order_by('nompren').exclude(etudiantid__in=dejasaisi)
    else:
        listet=Etudiant.objects.filter(Q(etudiantid__in=inscr) & Q(nompren__startswith=filtre)).order_by('nompren').exclude(etudiantid__in=dejasaisi)
    return render(request, 'notes3/inscritniveau.html',{'listes':listet})

class tmpnote_updateView(UpdateView):
    model=tmpnote
    template_suffix_name='_update_form'
    slug_field='idtmp'
    form_class=tnoteform
    template_name_suffix='_update_form'
    def get_success_url(self):
        return reverse_lazy('tmpnote')
    

class tmpnote_list(ListView):
    model=tmpnote
    template_name='notes3/tmpnote.html'
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        dejasaisi=tmpnote.objects.filter(etudiant__isnull=False).values('etudiant')
        note=tmpnote.objects.all().order_by('-etudiant__etudiantid','etudiant__nompren')
        context['note']=note
        return context
def import_notes_tmp(request):
    tmp=tmpnote.objects.filter(etudiant__isnull=False)
    
    for t in tmp:
        try:
            n=Notes_ecue.objects.create(etudiant=t.etudiant, composition=t.composition, note=t.notes)
            n.save()
            examid=t.composition.examen.id
            composition=t.composition
        except:
            pass
    t=tmpnote.objects.all()
    t.delete()
    composition.tsave=False
    composition.save()
    return HttpResponseRedirect(reverse('stats',args=(examid,)))




def printAdmisPdf(request,examid):
    
    buffer = io.BytesIO()
    response = HttpResponse(content_type = 'application/pdf')
    height,width=A4
    exam=Examen.objects.get(id=examid)
    filname='resultat_admis' +exam.ue.code+'_session_'+str(exam.session)+'.pdf'
    response['Content-Disposition'] = 'inline; filename = "'+filname+'"'
    admis=Resultat_info.objects.get(id=1)
    doc = SimpleDocTemplate(buffer,   pagesizes = landscape(A3))
    doc.pagesize = landscape(A3)
    exam=Examen.objects.get(id=examid)
    composition=Composition.objects.filter(examen=exam).order_by('ecue__code')
    etudiant=Notes_Ue.objects.filter(Q(examen=exam) & Q(resultat=admis)).order_by("-moyenne")
    data=[]
    header=["N°","NCE","Nom","Prenoms","Mention"]
    colWidths = [1*cm,   3*cm,   3*cm,   7.5*cm]
    sp = ParagraphStyle('parrafos',   
              alignment = TA_CENTER,  
              fontSize = 16,  
              fontName = "Times-Roman",
              leading = 20)
    
    colWidths.append(2.2*cm)
    data.append(header)
    j=1
    styles = getSampleStyleSheet()
    for et in etudiant:
        line=[]
        line.append(j)
        line.append(et.etudiant.nce)
        line.append(et.etudiant.nom)
        line.append(et.etudiant.prenoms)
        line.append(get_mention(et.moyenne))
        data.append(line)
        j=j+1
    story=[]
    t=Table(data,colWidths)
    t=Table(data,colWidths)
    filp = Paragraph("<b> UFR Sciences de la nature </b>",  sp)
    story.append(filp)
    filp = Paragraph("---------------------",  sp)
    story.append(filp)
    niv = Paragraph("<b>"+exam.niveau.labels+"</b>",  sp)
    story.append(niv)
    filp = Paragraph("--------------------- ",  sp)
    session = Paragraph("<b> Résultats des étudiants admis à la session: "+str(exam.session)+" de l'UE: " + exam.ue.labels+" ("+exam.ue.code+") par ordre alphabétique</b>",  sp)
    story.append(session)
    style = []
    style.append(('GRID',  (0,  0),  (-1,  -1),  0.5,  colors.black))
    filp = Paragraph("<b> *************************** </b>",  sp)
    story.append(filp)
    t.setStyle(TableStyle(style))
    story.append(t)
    spd = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 14,  
              fontName = "Times-Roman",  
              leading = 50)
    spn = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 14,  
              fontName = "Times-Roman")
    spnb1 = ParagraphStyle('parrafos',   
              fontSize = 10,  
              fontName = "Times-Roman")
    spnb2 = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 10,  
              fontName = "Times-Roman",  
              leading = 10)
    filp = Paragraph("<b>---------------------</b>",  spnb1)
    story.append(filp)
    nb = Paragraph("<b>NB: Vous disposez 3 jours pour entamer une procédure de reclamation à compter de la date de signature de ces résultats</b>",   spnb2)
    story.append(nb)
    ledoyen = Paragraph('<b>Le doyen</b>',   spd)
    story.append(ledoyen)
    nomdoyen = Paragraph('<b>TIHO Séydou</b>',   spn) 
    story.append(nomdoyen)
     
   
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def printAjournePdf(request,examid):
    
    buffer = io.BytesIO()
    response = HttpResponse(content_type = 'application/pdf')
    height,width=A4
    exam=Examen.objects.get(id=examid)
    filname='resultat' +exam.ue.code+'_session_'+str(exam.session)+'.pdf'
    response['Content-Disposition'] = 'inline; filename = "'+filname+'"'
    ajourne=Resultat_info.objects.get(id=3)
    doc = SimpleDocTemplate(buffer,   pagesizes = landscape(A3))
    doc.pagesize = landscape(A3)
    exam=Examen.objects.get(id=examid)
    composition=Composition.objects.filter(examen=exam).order_by('ecue__code')
    etudiant=Notes_Ue.objects.filter(Q(examen=exam) & Q(resultat=ajourne)).order_by("etudiant__nompren")
    data=[]
    header=["N°","NCE","Nom","Prenoms"]
    colWidths = [1*cm,   3*cm,   3*cm,   7.5*cm]
    sp = ParagraphStyle('parrafos',   
              alignment = TA_CENTER,  
              fontSize = 16,  
              fontName = "Times-Roman",
              leading = 20)
    for comp in composition:
        
        if comp.ano==True:
            header.append("a"+comp.ecue.code+comp.comptype.code)
            colWidths.append(2.5*cm)
            header.append(comp.ecue.code+comp.comptype.code)
            colWidths.append(2.5*cm)
        else:
            header.append(comp.ecue.code+comp.comptype.code)
            colWidths.append(2.5*cm)
   
    data.append(header)
    j=1
    styles = getSampleStyleSheet()
    for et in etudiant:
        line=[]
        line.append(j)
        line.append(et.etudiant.nce)
        line.append(et.etudiant.nom)
        line.append(et.etudiant.prenoms)
        for comp in composition:
            dt=Notes_ecue.objects.filter(Q(examen=exam) & Q(composition=comp) & Q(etudiant=et.etudiant)).order_by('ecue__code')
            if dt.exists:
                if comp.ano==True:
                    if dt[0].anonymat==None:
                        line.append('')
                        line.append('')
                    else:
                        line.append(dt[0].anonymat.ano) 
                        line.append(dt[0].note)      
                else:
                    line.append(dt[0].note)
            else:
                if compo.ano==True:
                    line.append('')
                    line.append('')
                    
                else:
                    line.append('')

        data.append(line)
        j=j+1
    story=[]
    t=Table(data,colWidths)
    filp = Paragraph("<b> UFR Sciences de la nature </b>",  sp)
    story.append(filp)
    filp = Paragraph("---------------------",  sp)
    story.append(filp)
    niv = Paragraph("<b>"+exam.niveau.labels+": </b>",  sp)
    story.append(niv)
    filp = Paragraph("--------------------- ",  sp)
    session = Paragraph("<b> Résultats des étudiant(e)s ajourné(e)s à la session: "+str(exam.session)+" de l'UE: " + exam.ue.labels+" ("+exam.ue.code+") par orde alphabétique</b>",  sp)
    story.append(session)
    style = []
    style.append(('GRID',  (0,  0),  (-1,  -1),  0.5,  colors.black))
    filp = Paragraph("<b> *************************** </b>",  sp)
    story.append(filp)
    t.setStyle(TableStyle(style))
    story.append(t)
    spd = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 14,  
              fontName = "Times-Roman",  
              leading = 50)
    spn = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 14,  
              fontName = "Times-Roman")
    spnb1 = ParagraphStyle('parrafos',   
              fontSize = 10,  
              fontName = "Times-Roman")
    spnb2 = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 10,  
              fontName = "Times-Roman",  
              leading = 10)
    filp = Paragraph("<b>---------------------</b>",  spnb1)
    story.append(filp)
    nb = Paragraph("<b>NB: Vous disposez 3 jours pour entamer une procédure de reclamation à compter de la date de signature de ces résultats</b>",   spnb2)
    story.append(nb)
    nb = Paragraph("<b>NB: Une moyenne accompgnées d'une astérix (*) signifie que l'étudiant(e) a été repêché(e) </b>",   spnb2)
    story.append(nb)
    ledoyen = Paragraph('<b>Le doyen</b>',   spd)
    story.append(ledoyen)
    nomdoyen = Paragraph('<b>TIHO Séydou</b>',   spn) 
    story.append(nomdoyen)
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def delib(examid):
    examen=Examen.objects.get(id=examid)
    admis=Resultat_info.objects.get(id=1)
    cm=Compotype.objects.get(id=1)
    tp=Compotype.objects.get(id=3)
    ajourne=Resultat_info.objects.get(id=3)
    if examen.afficher==False:
        Notes_Ue.objects.filter(Q(examen__id=examid) & Q(moyenne__gte=examen.delib_cm)).update(resultat=admis)
        Notes_Ue.objects.filter(Q(examen__id=examid) & Q(moyenne__lt=10) & Q(moyenne__gte=examen.delib_cm)).update(repeche=True)
        Notes_Ue.objects.filter(repeche=True).update(moyenne=10)
        Notes_Ue.objects.filter(Q(examen__id=examid) & Q(moyenne__lt=examen.delib_cm)).update(resultat=ajourne)
        Notes_Ue.objects.filter(Q(examen__id=examid) & Q(moyenne__lt=10) & Q(resultat=admis)).update(moyenne=10)                  
    else:
        Notes_Ue.objects.filter(Q(examen=examen) & Q(moyenne__gte=examen.delib_cm) & Q(reclamation=True)).update(resultat=admis)
        Notes_Ue.objects.filter(Q(examen__id=examid) & Q(moyenne__lt=10) & Q(moyenne__gte=examen.delib_cm) & Q(reclamation=True)).update(repeche=True)
        Notes_Ue.objects.filter(repeche=True).update(moyenne=10)
        ajourne=Resultat_info.objects.get(id=3)
        Notes_Ue.objects.filter(Q(examen__id=examid) & Q(moyenne__lt=examen.delib_cm) & Q(reclamation=True)).update(resultat=ajourne)
        Notes_Ue.objects.filter(Q(examen__id=examid) & Q(moyenne__lt=10) & Q(resultat=admis)).update(moyenne=10)
        
                    


def testResultat(request, examid):
    examen=Examen.objects.get(id=examid)
    delib(examid)
    buffer = io.BytesIO()
    response = HttpResponse(content_type = 'application/pdf')
    height,width=A4
    exam=Examen.objects.get(id=examid)
    if exam.afficher==True:
        filname='resultat_reclamation_'+ exam.niveau.code+'_'+exam.ue.code+'_session_'+str(exam.session)+'_'+exam.niveau.filiere.anuniv.labels+'.pdf'
    else:
        filname='resultat'+ exam.niveau.code+'_'+exam.ue.code+'_session_'+str(exam.session)+'_'+exam.niveau.filiere.anuniv.labels+'.pdf'
    response['Content-Disposition'] = 'inline; filename = "'+filname+'"'
    admis=Resultat_info.objects.get(id=1)
    doc = SimpleDocTemplate(buffer,   pagesizes = landscape(A3))
    doc.pagesize = landscape(A3)    
    doc.bottomMargin=0*cm                                       
    doc.topMargin=1*cm                                  
    doc.leftMargin=0*cm
    doc.rightMargin=0*cm
    exam=Examen.objects.get(id=examid)
    composition=Composition.objects.filter(examen=exam).order_by('ecue__code')
    cfcs=Notes_Ue.objects.filter(Q(examen=examen)).values('etudiant__cfc').distinct('etudiant__cfc')
    story=[]
    for cfc in cfcs:
        c=cfc['etudiant__cfc']
        
        if exam.afficher==False:
            etudiant=Notes_Ue.objects.filter(Q(examen=exam) & Q(resultat=admis) & Q(etudiant__nom__isnull=False) & Q(etudiant__cfc=c)).order_by("etudiant__nompren")
        else:
            etudiant=Notes_Ue.objects.filter(Q(examen=exam) & Q(resultat=admis) & Q(etudiant__nom__isnull=False) & Q(reclamation=True) & Q(etudiant__cfc=c)).order_by("etudiant__nompren")
        data=[]
        header=["N°","NCE","Nom","Prenoms","Mention"]
        colWidths = [1*cm,   3*cm,   3*cm,   7.5*cm]
        sp = ParagraphStyle('parrafos',   
              alignment = TA_CENTER,  
              fontSize = 16,  
              fontName = "Times-Roman",
              leading = 20)
        colWidths.append(2.2*cm)
        data.append(header)
        j=1
        styles = getSampleStyleSheet()
        for et in etudiant:
            line=[]
            line.append(j)
            line.append(et.etudiant.nce)
            line.append(et.etudiant.nom)
            line.append(et.etudiant.prenoms)
            line.append(get_mention(et.moyenne))
            data.append(line)
            j=j+1
        t=Table(data,colWidths)
        t=Table(data,colWidths)
        if c==True or c == None:
            filp = Paragraph("<b> Centre de Formation Continue (CFC)</b>",  sp)
        if c==False:
            filp = Paragraph("<b> UFR Sciences de la nature </b>",  sp)
        story.append(filp)
        filp = Paragraph("---------------------",  sp)
        story.append(filp)
        niv = Paragraph("<b>"+exam.niveau.labels+"</b>",  sp)
        story.append(niv)
        filp = Paragraph("--------------------- ",  sp)
        if exam.afficher==False or exam.afficher==None:
            session = Paragraph("<b> Résultats des étudiants admis à la session: "+str(exam.session)+" de l'UE: " + exam.ue.labels+" ("+exam.ue.code+") par ordre alphabétique</b>",  sp)
        if exam.afficher==True:
            session = Paragraph("<b> Résultats des étudiants admis après réclamation à la session: "+str(exam.session)+" de l'UE: " + exam.ue.labels+" ("+exam.ue.code+") par ordre alphabétique</b>",  sp)
        story.append(session)
        style = []
        style.append(('GRID',  (0,  0),  (-1,  -1),  0.5,  colors.black))
        filp = Paragraph("<b> *************************** </b>",  sp)
        story.append(filp)
        t.setStyle(TableStyle(style))
        story.append(t)
        spd = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 14,  
              fontName = "Times-Roman",  
              leading = 50)
        spn = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 14,  
              fontName = "Times-Roman")
        spnb1 = ParagraphStyle('parrafos',   
              fontSize = 10,  
              fontName = "Times-Roman")
        spnb2 = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 10,  
              fontName = "Times-Roman",  
              leading = 10)
        filp = Paragraph("<b>---------------------</b>",  spnb1)
        story.append(filp)
        nb = Paragraph("<b>NB: Vous disposez trois jours pour entamer une procédure de reclamation à compter de la date de signature de ces résultats</b>",   spnb2)
        story.append(nb)
        ledoyen = Paragraph('<b>Le doyen</b>',   spd)
        story.append(ledoyen)
        nomdoyen = Paragraph('<b>TIHO Séydou</b>',   spn) 
        story.append(nomdoyen)
        story.append(PageBreak())
        ajourne=Resultat_info.objects.get(id=3)
        exam=Examen.objects.get(id=examid)
        composition=Composition.objects.filter(examen=exam).order_by('ecue__code')
        recomp=Notes_Ue.objects.filter(Q(examen__niveau=exam.niveau) & Q(examen__ue=exam.ue) & Q(examen__session=1) &Q(resultat__id=6)).values('etudiant')
        if exam.afficher==True:
            etudiant=Notes_Ue.objects.filter(Q(examen=exam) & Q(resultat=ajourne) & Q(etudiant__nom__isnull=False) & Q(reclamation=True) & Q(etudiant__cfc=c)).order_by("etudiant__nompren")
        else:
            etudiant=Notes_Ue.objects.filter(Q(examen=exam) & Q(resultat=ajourne) & Q(etudiant__nom__isnull=False) & Q(etudiant__cfc=c)).exclude(etudiant__in=recomp).order_by("etudiant__nompren")
        data=[]
        header=["N°","NCE","Nom","Prenoms"]
        colWidths = [1*cm,   3*cm,   3*cm,   7.5*cm]
        sp = ParagraphStyle('parrafos',   
              alignment = TA_CENTER,  
              fontSize = 16,  
              fontName = "Times-Roman",
              leading = 20)
        for comp in composition:
            if comp.ano==True:
                header.append("a"+comp.ecue.code+comp.comptype.code)
                colWidths.append(2.5*cm)
                header.append(comp.ecue.code+comp.comptype.code)
                colWidths.append(2.5*cm)
            else:
                header.append(comp.ecue.code+comp.comptype.code)
                colWidths.append(2.5*cm)
   
        data.append(header)
        j=1
        styles = getSampleStyleSheet()
        for et in etudiant:
            line=[]
            line.append(j)
            line.append(et.etudiant.nce)
            line.append(et.etudiant.nom)
            line.append(et.etudiant.prenoms)
            for comp in composition:
            
            
                dt=Notes_ecue.objects.filter(Q(examen=exam) & Q(composition=comp) & Q(etudiant=et.etudiant)).order_by('ecue__code')
            
                if dt.exists:
                    if comp.ano==True:
                        if dt[0].anonymat==None:
                            line.append('')
                            line.append('')
                        else:
                            line.append(dt[0].anonymat.ano) 
                            line.append(dt[0].note)      
                    else:
                        line.append(dt[0].note)
                else:
                    if compo.ano==True:
                        line.append('')
                        line.append('')
                    else:
                        line.append('')

            data.append(line)
            j=j+1
        t=Table(data,colWidths)
        if c==True or c == None:
            filp = Paragraph("<b> Centre de Formation Continue (CFC)</b>",  sp)
        if c==False:
            filp = Paragraph("<b> UFR Sciences de la nature </b>",  sp)
        story.append(filp)
        filp = Paragraph("---------------------",  sp)
        story.append(filp)
        niv = Paragraph("<b>"+exam.niveau.labels+": </b>",  sp)
        story.append(niv)
        filp = Paragraph("--------------------- ",  sp)
        if exam.afficher==True:
            session = Paragraph("<b> Résultats des étudiant(e)s ajourné(e)s après réclamation à la session: "+str(exam.session)+" de l'UE: " + exam.ue.labels+" ("+exam.ue.code+") par ordre alphabétique</b>",  sp)
        else:
            session = Paragraph("<b> Résultats des étudiant(e)s ajourné(e)s à la session: "+str(exam.session)+" de l'UE: " + exam.ue.labels+" ("+exam.ue.code+") par ordre alphabétique</b>",  sp)
        story.append(session)
        style = []
        style.append(('GRID',  (0,  0),  (-1,  -1),  0.5,  colors.black))
        filp = Paragraph("<b> *************************** </b>",  sp)
        story.append(filp)
        t.setStyle(TableStyle(style))
        story.append(t)
        splft = ParagraphStyle('parrafos',   
              alignment = TA_LEFT,  
              fontSize = 14,  
              fontName = "Times-Roman",  
              leading = 20)
        spd = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 14,  
              fontName = "Times-Roman",  
              leading = 50)
        spn = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 14,  
              fontName = "Times-Roman")
        spnb1 = ParagraphStyle('parrafos',   
              fontSize = 10,  
              fontName = "Times-Roman")
        spnb2 = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 10,  
              fontName = "Times-Roman",  
              leading = 10)
        filp = Paragraph("<b>---------------------</b>",  spnb1)
        story.append(filp)
        nb = Paragraph("<b>NB: Vous disposez trois jours pour entamer une procédure de reclamation à compter de la date de signature de ces résultats</b>",   spnb2)
        story.append(nb)
        composition=Composition.objects.filter(examen=exam).order_by('ecue').distinct('ecue')
        for c in composition:
            nb=Paragraph(c.ecue.code+": "+c.ecue.labels,splft)
            story.append(nb)
        ledoyen = Paragraph("<b>Le Directeur de l'UFR</b>",   spd)
        story.append(ledoyen)
        nomdoyen = Paragraph('<b>TIHO Séydou</b>',   spn) 
        story.append(nomdoyen)
        story.append(PageBreak())
    exam=Examen.objects.get(id=examid)
    if exam.afficher==True:
        sujet='Listing de résultats  après réclamation de '+exam.ue.code
        message="Le listing des résultats de la session " + str(exam.session) + " de "+ exam.ue.code +"("+exam.niveau.code+") sont disponibles à l'ufr sn.\n"
    else:
        sujet='Listing de résultats de '+exam.ue.code
        message="Le listing des résultats de la session " + str(exam.session) + " de "+ exam.ue.code +"("+exam.niveau.code+") sont disponibles à l'ufr sn.\n"
    exam.afficher=True
    exam.save()
    try:
        send_email_to(sujet,message,exam.niveau.nivid,examid)
    except:
        pass
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response


def moveano(request,ano):
    ano=Anonymat.objects.get(ano=ano)
    comp=ano.composition
    exam=comp.examen
    compolist=Composition.objects.filter(examen=exam).exclude(compid=comp.compid)
    context={}
    context['ano']=ano
    context['composition']=comp
    context['compolist']=compolist

    return render(request,'notes3/anonymat_move.html',context)



def anomoved(request,ano):
    if request.method=="POST":
        compid=request.POST['compo']
        composition=Composition.objects.get(compid=compid)
        ano=Anonymat.objects.get(ano=ano)
        ano.composition=composition
        ano.save()
        return HttpResponseRedirect(reverse('anolist',args=(compid,)))
    else:
        return HttpResponseRedirect(reverse('anolist',args=(compid,)))



def reclamation(request, ano):
    ano=Anonymat.objects.get(ano=ano)
    composition=ano.com
    examen=Examen.objects.get(id=examid)
    composition=Composition.objects.filter(examen=examen)


def getanonymat(request):
    composition=request.GET.get("composition_id")
    
    etudiantid=request.GET.get("etudiant_id")
    etudiant=Etudiant.objects.get(etudiantid=etudiantid)
    ano=Anonymat.objects.filter(Q(composition=composition) & Q(etudiant=etudiant)).values('ano')
    note=Notes_ecue.objects.filter(Q(composition=composition) & Q(etudiant=etudiant)).values('note')
    context={}
    if ano:
        context['ano']=ano[0]['ano']
    if note:
        context['note']=note[0]['note']
    return JsonResponse(context)


def get_composition_ano_alert(request):
    fano=etudiantid=request.GET.get("fano")
    lano=etudiantid=request.GET.get("fano")
    Anox=Anonymat.objects.filter(Q(ano__gte=fano) & Q(ano__lte=lano)).distinct('composition').values('composition').count()
    compo=Anonymat.objects.filter(Q(ano__gte=fano) & Q(ano__lte=lano)).distinct('composition').values('composition')
    print(compo)
    context={}
    id=compo[0]['composition']
    compo=Composition.objects.get(compid=id)
    if Anox:
        context['composition']=compo.ecue.code+' de '+compo.examen.niveau.code
        context['alert']=True
    else:
        context['alert']=False
    return JsonResponse(context)




class ue_update(UpdateView):
    model=Ue
    template_name_suffix="_update_form"
    form_class=ueform
    slug_field='ueid'


class ue_create(CreateView):
    model=Ue
    template_name='notes3/ue_create.html'
    form_class=ueAddform
    def get_initial(self):
        initial=super(ue_create, self).get_initial()
        initial=initial.copy()
        initial['niveau']=self.kwargs['nivid']
        max_id=Ue.objects.filter(niveau__nivid=self.kwargs['nivid']).aggregate(max=Max('ueid'))
        initial['ueid']=max_id['max']+1
        return initial

class ecue_update(UpdateView):
    model=UeInfo
    template_name_suffix='_update_form'
    form_class=ecueform
    slug_field='uei'

class ecue_create(CreateView):
    model=Ue
    template_name='notes3/ecue_create.html'
    form_class=addecueform
    def get_initial(self):
        initial=super(ecue_create, self).get_initial()
        initial=initial.copy()
        initial['ueid']=self.kwargs['ueid']
        ecue=UeInfo.objects.filter(ue__ueid=self.kwargs['ueid'])
        initial['ue']=Ue.objects.get(ueid=self.kwargs['ueid'])
        initial['niveau']=Ue.objects.get(ueid=self.kwargs['ueid']).niveau
        if ecue:
            max_id=UeInfo.objects.filter(ue__ueid=self.kwargs['ueid']).aggregate(max=Max('uei'))
            initial['uei']=max_id['max']+1
        else:
            initial['uei']=self.kwargs['ueid']*10+1
        return initial

def send_email_to(sujet,message,nivid,examid):
    to_list=['danhofr@gmail.com','setiho@hotmail.com','eloik@yahoo.fr','ahuerod.inf@univ-na.ci ']
    niveau=Niveau.objects.get(nivid=nivid)
    emailrep=niveau.responsable
    message=message+" Les résultats des ues suivantes de "+niveau.code+":\n"
    examen_afficher=Examen.objects.filter(Q(niveau=niveau) & Q(anuniv__auid=1718) & Q(afficher=True))
    for exam in examen_afficher:
        message=message+"\t -"+exam.ue.code+"\n"
    message=message+" sont disponibles.\n"
    message=message+"Ce message est généré automatiquement par le système"
    if email==None:
        pass
    else:
        to_list.append(emailrep)
    email=EmailMessage(sujet,
        message,
        to=to_list
    )
    exam=Examen.objects.get(id=examid)
    filename='/home/ufr-sn/Documents/bd/deliberation/'+exam.niveau.code+'/délibératin' +'_'+exam.niveau.code+'_'+exam.ue.code+'_session_'+str(exam.session)+'.pdf'


    email.send()

def prevenir(request,compoid):
    send_ecue_ano(compoid)
    composition=Composition.objects.get(compid=compoid)
    examid=composition.examen.id
    return HttpResponseRedirect(reverse('detexam', args=[examid,]))


def send_ecue_ano(compid):
    to_list=['danhofr@gmail.com','setiho@hotmail.com','eloik@yahoo.fr','ahuerod.inf@univ-na.ci ']
    compo=Composition.objects.get(compid=compid)
    niveau=compo.examen.niveau
    email=niveau.responsable
    sujet='Suivie de la saisie des anonymats'
    message=" Les anonymat de " + compo.ecue.labels +"("+compo.ecue.code +") de l'"+compo.ecue.ue.labels+" ont été  complètement saisies.\n Nous n'attendons que les notes\n"
    if email==None:
        pass
    else:
        to_list.append(email)
    email=EmailMessage(sujet,
        message,
        to=to_list
    )
    email.send()

def notusedano(request):
    compo=request.GET.get('composition_id')
    composition=Composition.objects.get(compid=compo)
    used_ano=Notes_ecue.objects.filter(Q(composition=composition)).values_list('anonymat')
    ano_not_used=Anonymat.objects.filter(Q(composition=composition)).exclude(ano__in=used_ano)
    context={}
    context['ano']=ano_not_used
    return  render(request,'notes3/liste_anonymat.html',context)


def liste_etudiant_deja(request):
    compo=request.GET.get('composition_id')
    composition=Composition.objects.get(compid=compo)
    filtre=request.GET.get('filtre')
    if composition.ano==True:
        used_etudiant=Anonymat.objects.filter(Q(composition=composition)).values_list('etudiant')
    else:
        used_etudiant=Inscription.objects.filter(niveau=composition.examen.niveau).values_list('etudiant')
    if filtre==None:
        list=Etudiant.objects.filter(etudiantid__in=used_etudiant).order_by('nom','prenoms')

    else:
        list=Etudiant.objects.filter(Q(etudiantid__in=used_etudiant) & Q(nompren__contains=filtre)).order_by('nom','prenoms')
    if composition.ano==False:
        dejasaisi=Notes_ecue.objects.filter(composition=composition).values_list('etudiant')
        list=list.exclude(etudiantid__in=dejasaisi) 
    return render(request, 'notes3/inscritniveau.html',{'listes':list})


def recalculate(request,examid):
    exam=Examen.objects.get(id=examid)
    check_reclamation(examid)
    compcount=Composition.objects.filter(examen=exam).count()
    etudx=Notes_ecue.objects.filter(Q(reclamation=True) & Q(examen=exam)).distinct('etudiant').values('etudiant')

    if exam.afficher==False:
        note_etudiant=Notes_ecue.objects.values('etudiant').annotate(num_et=Count('etudiant')).filter(Q(examen=exam) & Q(num_et__lt=compcount)).order_by('etudiant__nompren','num_et')
    else:
        note_etudiant=Notes_ecue.objects.values('etudiant').annotate(num_et=Count('etudiant')).filter(Q(examen=exam) & Q(num_et__lt=compcount) & Q(etudiant__in=etudx)).order_by('etudiant__nompren','num_et')
    if note_etudiant:
        
        return HttpResponseRedirect(reverse('stats', args=[examid,]))
    else:
        return HttpResponseRedirect(reverse('calculate', args=[examid,]))



def checkcoef_calcmode(examid):
    examen=Examen.objects.get(id=examid)
    cycle=examen.niveau.cycle
    tp=Compotype.objects.get(id=3)
    nbtp=Composition.objects.filter(Q(examen=examen) & Q(comptype=tp)).count()
    cm=Compotype.objects.get(id=1)
    nbcm=Composition.objects.filter(Q(examen=examen) & Q(comptype=cm)).count()
    examen.nbtp=nbtp
    examen.nbcm=nbcm
    examen.save()
    nbcm=examen.nbcm
    nbtp=examen.nbtp
    nbtd=examen.nbtd
    if cycle==1:
        examen.niveau.coefcm=3
        examen.niveau.coeftd=1
        examen.niveau.coeftp=2
        examen.coefcm=2
        examen.coeftp=1
    if cycle==2:
        examen.niveau.coefcm=3
        examen.niveau.coeftd=1
        examen.niveau.coeftp=2
        examen.coefcm=1
        examen.coeftp=1

    if nbcm>0  and nbtp>0:
        examen.calcmode=2
    if nbcm>0  and nbtp==0:
        examen.calcmode=1
    examen.save()
    compos=Composition.objects.filter(examen=examen)
    for c in compos:
        if c.comptype.id==1:
            coefficient=examen.niveau.coefcm
        if c.comptype.id==2:
            coefficient=examen.niveau.coeftd
        if c.comptype.id==3:
            coefficient=examen.niveau.coeftp
        c.save()


def link_cmtd(examid):
    examen=Examen.objects.get(id=examid)
    td=Compotype.objects.get(id=2)
    cm=Compotype.objects.get(id=1)
    compo_cm=Composition.objects.filter(Q(examen=examen) & Q(comptype=cm))
    for c in compo_cm:        
            tdx=Composition.objects.filter(Q(examen=examen) & Q(ecue__code=c.ecue.code) & Q(comptype=td))
            for tx in tdx:
                obj,created=Link_cm_td.objects.update_or_create(
                    composition=c,
                    linked_td=tx,
                )
      
def check_moyenne_ecue_cm(examid):
    examen=get_object_or_404(Examen,Q(id=examid))
    compos=Composition.objects.filter(examen=examen)
    cm=Compotype.objects.get(id=1)
    td=Compotype.objects.get(id=2)
    tp=Compotype.objects.get(id=3)
    ctd=Composition.objects.filter(Q(examen=examen) & Q(comptype=td)).count()
    for c in compos:
        if examen.session==2:
            if c.comptype==cm or c.comptype==tp:
                report_notes(c.compid)
        if c.comptype==cm:
            calc_moy_cm_ecue(c.compid,examid)

def calc_moy_cm_ecue(compid,examid):
    checkcoef_calcmode(examid)
    myids=[]
    link_cmtd(examid)
    myids.append(compid)
    examen=Examen.objects.get(id=examid)
    compo=Composition.objects.get(compid=compid)
    cm=get_object_or_404(Composition,Q(compid=compid))
    if examen.afficher==False:
        Notes_ecue.objects.filter(Q(examen=examen) & Q(note__lt=0)).update(note=0)
        Notes_ecue.objects.filter(Q(examen=examen) & Q(notepond__lt=0)).update(notepond=0)
    else:
        Notes_ecue.objects.filter(Q(examen=examen) & Q(note__lt=0) & Q(reclamation=True)).update(note=0)
        Notes_ecue.objects.filter(Q(examen=examen) & Q(notepond__lt=0) & Q(reclamation=True)).update(notepond=0)
    td_list=Link_cm_td.objects.filter(composition=cm).values_list('linked_td__compid')
    if examen.session==1:
        for id in td_list:
            myids.append(id[0])
    sumcoef=Composition.objects.filter(compid__in=myids).aggregate(Sum('coefficient'))
    if examen.afficher==True:
        etlist=Notes_ecue.objects.filter(Q(examen=examen) & Q(reclamation=True)).distinct('etudiant').values_list('etudiant')
        sumnote=Notes_ecue.objects.values('etudiant').filter(Q(composition__compid__in=myids) & Q(etudiant__in=etlist)).annotate(sumnote=Sum('notepond'))    
        m=Moyenne_ecue_cm.objects.filter(Q(examen=examen) & Q(composition=compo) & Q(etudiant__in=etlist))
    else:
        sumnote=Notes_ecue.objects.values('etudiant').filter(composition__compid__in=myids).annotate(sumnote=Sum('notepond'))    
        m=Moyenne_ecue_cm.objects.filter(Q(examen=examen) & Q(composition=compo))
    if m:
            m.delete()
    for s in sumnote:
        etudiantid=s['etudiant']
        etx=Etudiant.objects.get(etudiantid=etudiantid)
        if examen.afficher==True:
            m=Moyenne_ecue_cm.objects.create(etudiant=etx,examen=examen,composition=cm,sumcmtd=s['sumnote'],coefsum=sumcoef['coefficient__sum'],reclamation=True)
        else:
            m=Moyenne_ecue_cm.objects.create(etudiant=etx,examen=examen,composition=cm,sumcmtd=s['sumnote'],coefsum=sumcoef['coefficient__sum'])
        m.save()
    

def check_reclamation(examid):
    print('check reclamation......')
    examen=get_object_or_404(Examen,Q(id=examid))
    Moyenne_ecue_cm.objects.filter(Q(examen=examen)).update(reclamation=False)
    etudiant_list=Notes_ecue.objects.filter(Q(examen=examen) & Q(reclamation=True)).distinct('etudiant').values_list('etudiant')
    Moyenne_ecue_cm.objects.filter(Q(examen=examen) & Q(etudiant__in=etudiant_list)).update(reclamation=True)
    Moyenne_ue_tp.objects.filter(Q(examen=examen) & Q(etudiant__in=etudiant_list)).update(reclamation=True)
    Moyenne_ue_cm.objects.filter(Q(examen=examen) & Q(etudiant__in=etudiant_list)).update(reclamation=True)
    Notes_Ue.objects.filter(Q(examen=examen) & Q(etudiant__in=etudiant_list)).update(reclamation=True)
    if examen.calcmode==2:
        Moyenne_Ue.objects.filter(Q(examen=examen) & Q(etudiant__in=etudiant_list)).update(reclamation=True)

def calc_moy_tp_ue(examid):
    print("calcul des moyennes de Tp...")
    examen=Examen.objects.get(id=examid)
    checkcoef_calcmode(examid)
    tp=Compotype.objects.get(id=3)
    sumcoef=Composition.objects.filter(Q(examen=examen) & Q(comptype=tp)).aggregate(sumcoef=Sum('coefficient'))
    compos=Composition.objects.filter(Q(examen=examen) & Q(comptype=tp))
    
    if examen.afficher==True:
        sumnote=Notes_ecue.objects.values('etudiant').filter(Q(composition__in=compos) & Q(reclamation=True)).annotate(sumnote=Sum('notepond')) 
        mx=Moyenne_ue_tp.objects.filter(Q(examen=examen) & Q(reclamation=True))
    else:
        sumnote=Notes_ecue.objects.values('etudiant').filter(composition__in=compos).annotate(sumnote=Sum('notepond')) 
        mx=Moyenne_ue_tp.objects.filter(examen=examen)
    if mx:
        mx.delete()
    for s in sumnote:
            etudiantid=s['etudiant']
            etx=Etudiant.objects.get(etudiantid=etudiantid)
            if examen.afficher==True:
                m=Moyenne_ue_tp.objects.create(etudiant=etx,examen=examen,sumtp=s['sumnote'],coefsum=sumcoef['sumcoef'],reclamation=True)
            else:
                m=Moyenne_ue_tp.objects.create(etudiant=etx,examen=examen,sumtp=s['sumnote'],coefsum=sumcoef['sumcoef'])
            m.save()
            

def calc_moy_cm_ue(examid):
    print("calcul des moyennes de CM...")
    examen=Examen.objects.get(id=examid)
    calcmode=examen.calcmode
    
    coef=0
    cm=Compotype.objects.get(id=1)
    coefs=Moyenne_ecue_cm.objects.filter(Q(examen=examen)) .distinct('composition')
  
    for c in coefs:
            coef=c.coefcm+coef
    if examen.afficher==True:
        etlist=Moyenne_ecue_cm.objects.filter(Q(examen=examen) & Q(reclamation=True)).distinct('etudiant').values_list('etudiant')
        sumnote=Moyenne_ecue_cm.objects.values('etudiant').filter(Q(examen=examen) & Q(reclamation=True)).annotate(sumnote=Sum('moypond'))
        mx=Moyenne_ue_cm.objects.filter(Q(examen=examen) & Q(etudiant__in=etlist))
    else:
        sumnote=Moyenne_ecue_cm.objects.values('etudiant').filter(examen=examen).annotate(sumnote=Sum('moypond'))
        mx=Moyenne_ue_cm.objects.filter(examen=examen)
    if mx:
        mx.delete()
    for s in sumnote:
            etudiantid=s['etudiant']
            etx=Etudiant.objects.get(etudiantid=etudiantid)
            if examen.afficher==True:
                m=Moyenne_ue_cm.objects.create(etudiant=etx,examen=examen,sumcm=s['sumnote'],coefsum=coef,reclamation=True)
            else:
                m=Moyenne_ue_cm.objects.create(etudiant=etx,examen=examen,sumcm=s['sumnote'],coefsum=coef)
            m.save()
    



def calculate2(request,examid):
    examen=Examen.objects.get(id=examid)
    checkcoef_calcmode(examid)
    check_moyenne_ecue_cm(examid)
    if examen.calcmode==1:
        calc_moy_cm_ue(examid)
        if examen.afficher==True:
            moyenne=Moyenne_ue_cm.objects.filter(Q(examen=examen) & Q(reclamation=True))
            n=Notes_Ue.objects.filter(Q(examen=examen) & Q(reclamation=True))
            if n:
                n.delete()
        else:
            moyenne=Moyenne_ue_cm.objects.filter(Q(examen=examen))
            n=Notes_Ue.objects.filter(examen=examen)
            if n:
                n.delete()
        for m in moyenne:
        
            Notes_Ue.objects.create(
                    etudiant=m.etudiant,
                    examen=m.examen,
                    moyenne=m.moyenne
                )
    if examen.calcmode==2:
        calc_moy_cm_ue(examid)
        calc_moy_tp_ue(examid)
        nx=Moyenne_tmp_cmtp.objects.all()
        nx.delete()
        if examen.afficher==True:
            notecm=Moyenne_ue_cm.objects.filter(Q(examen=examen) & Q(reclamation=True))
        else:
            notecm=Moyenne_ue_cm.objects.filter(examen=examen)
        cm=Compotype.objects.get(id=1)
        for n in notecm:
            m=Moyenne_tmp_cmtp.objects.create(etudiant=n.etudiant,examen=examen,comptype=cm,moyenne=n.moyenne,coefficient=examen.coefcm)
            m.save()
        if examen.afficher==True:
            notetp=Moyenne_ue_tp.objects.filter(Q(examen=examen) & Q(reclamation=True))
        else:
            notetp=Moyenne_ue_tp.objects.filter(examen=examen)
        tp=Compotype.objects.get(id=3)
        for n in notetp:
            m=Moyenne_tmp_cmtp.objects.create(etudiant=n.etudiant,examen=examen,comptype=tp,moyenne=n.moyenne,coefficient=examen.coeftp)
            m.save()
        coef=examen.coefcm+examen.coeftp
        sumnote=Moyenne_tmp_cmtp.objects.values('etudiant').filter(examen=examen).annotate(sumnote=Sum('moypond'))
        nx=Moyenne_Ue.objects.filter(examen=examen)
        if nx:
            nx.delete()
        for s in sumnote:
            m=Moyenne_Ue.objects.create(
                etudiant=Etudiant.objects.get(etudiantid=s['etudiant']),
                examen=examen,
                somme=s["sumnote"],coefficient=coef
            )
            m.save()
            
        if examen.afficher==True:
            moyenne=Moyenne_Ue.objects.filter(Q(examen=examen) & Q(reclamation=True))
            n=Notes_Ue.objects.filter(Q(examen=examen) & Q(reclamation=True))
            if n:
                n.delete()
        else:
            moyenne=Moyenne_Ue.objects.filter(Q(examen=examen))
            n=Notes_Ue.objects.filter(examen=examen)
            if n:
                n.delete()
        for m in moyenne:
            nx=Notes_Ue.objects.create(
                    etudiant=m.etudiant,
                    examen=m.examen,
                    moyenne=m.moyenne
                )
            nx.save()
    examen.calcul=True
    
    if examen.afficher==True:
        compos=Composition.objects.filter(examen=examen)
        for c in compos:
            etrecalm=Notes_ecue.objects.filter(Q(composition=c) & Q(reclamation=True)).values_list('etudiant')
            Notes_Ue.objects.filter(Q(etudiant__in=etrecalm) & Q(examen=c.examen)).update(reclamation=True)
        return HttpResponseRedirect(reverse('prttest', args=[examid,]))
    else:
        examen.calcul=True
        return HttpResponseRedirect(reverse('detexam', args=[examid,]))







def convert_true_yes(reclam):
    if reclam==True:
        return "OUI"
    if reclam==False or reclam==None:
        return "NON"

def export_ajourne_to_excel(request, examid):
    response = HttpResponse(content_type='text/csv')
    examen=Examen.objects.get(id=examid)
    ajourne=Resultat_info.objects.get(id=3)
    ajourne=Notes_Ue.objects.filter(Q(examen=examen) & Q(resultat=ajourne)).order_by('etudiant__nompren')  
    filename='/home/ufr-sn/Documents/listing_ajourne/'+examen.niveau.code+examen.ue.code+"session"+str(examen.session)+".csv"
    response['Content-Disposition'] = 'attachment; filename="'+filename+'"'
    f=open(filename,'w')
    writer=csv.writer(f, delimiter=';')
    writer.writerow(["Liste des ajourne de :",examen.ue.labels,"session",examen.session])
    writer.writerow([''])
    complist=Composition.objects.filter(examen=examen).order_by("ecue__code")
    entete=["ORDRE","NCE","NOM","PRENOMS","DATE DE NAISSANCE","LIEU DE NAISSANCE","RECLAMATION"]
    for c in complist:
        entete.append(c.ecue.code+c.comptype.code)
        if c.ano==True:
            entete.append("A"+c.ecue.code+c.comptype.code)
    writer.writerow(entete)
    j=1
    for et in ajourne:
        line=[j,et.etudiant.nce,et.etudiant.nom,et.etudiant.prenoms,et.etudiant.ddnais,et.etudiant.lnais,convert_true_yes(et.reclamation) ]
        for c in complist:
            notes_et=Notes_ecue.objects.filter(Q(composition=c) & Q(etudiant=et.etudiant))
            for n in notes_et:
                line.append(n.note)
                if n.anonymat==None:
                    line.append('')
                else:
                    line.append(n.anonymat)
        writer.writerow(line)             
        j=j+1
    f.close()
    return HttpResponseRedirect(reverse('ajourne_email',args=(examid,)))



def send_email_ajourne_to(request,examid):
    to_list=['danhofr@gmail.com','setiho@hotmail.com','eloik@yahoo.fr','ahuerod.inf@univ-na.ci ']
    examen=Examen.objects.get(id=examid)
    email=examen.niveau.responsable
    conseiller=examen.niveau.conseiller
    sujet="Listing des ajournés de "+examen.ue.code
    message=" Listing des ajournés de "+examen.niveau.code+":\n"
    if email==None:
        pass
    else:
        to_list.append(email)
        to_list.append(conseiller)
    email=EmailMessage(sujet,
        message,
        to=to_list
    )
    filename='/home/ufr-sn/Documents/listing_ajourne/'+examen.niveau.code+examen.ue.code+"session"+str(examen.session)+".csv"
    email.attach_file(filename)
    email.send()
    return HttpResponseRedirect(reverse('detexam',args=(examid,)))




class Inscription_create(CreateView):
    model=Inscription
    form_class=iForms
    template_name="notes3/inscriptions.html"
    def get_initial(self):
        initial=super(Inscription_create, self).get_initial()
        initial=initial.copy()
        initial['anuniv']=self.kwargs['auid']
        initial['niveau']=self.kwargs['niveauid']

        return initial
    def get_success_url(self):
        niveauid=self.kwargs['niveauid']
        auid=self.kwargs['auid']
        return reverse_lazy( 'einscrire', kwargs={'auid':auid,'niveauid': niveauid})
    def get_context_data(self, **kwargs):
        context=super(Inscription_create,self).get_context_data(**kwargs)
        auid=self.kwargs['auid']
        niveauid=self.kwargs['niveauid']
        context['niveauid']=niveauid
        context['curau']=auid
        return context


def view_pv(request,nivid):
    curau=get_object_or_404(AnUniv,Q(curau=True))
    return render(
        request,
        'notes3/pv.html',
        {
            'niveau':nivid,
            'curau':curau.auid,
        }
    )





def statistiques(request):
    auniv=AnUniv.objects.get(auid=1718)
    examen=Notes_Ue.objects.filter(resultat__isnull=True).distinct('examen')
    for e in examen:
        try:
            admis=Resultat_info.objects.get(id=1)
            Notes_Ue.objects.filter(Q(examen=e.examen) & Q(moyenne__gte=e.examen.delib)).update(resultat=admis)
            ajourne=Resultat_info.objects.get(id=3)
            Notes_Ue.objects.filter(Q(examen=e.examen) & Q(moyenne__lt=e.examen.delib)).update(resultat=ajourne)
            Notes_Ue.objects.filter(Q(examen=e.examen) & Q(moyenne__lt=10) & Q(resultat=admis)).update(moyenne=10)
        except:
            pass
          
    return HttpResponse('test')


def makepv2(request,nivid):
    #notes_ue_moypond_clean(nivid)
    curau=get_object_or_404(AnUniv,curau=True)
    niveau=Niveau.objects.all()
    entete=['NUM.','NCE','NOM et PRENOMS']
    niveau=Niveau.objects.get(nivid=nivid)
    filename='/home/ufr-sn/Documents/listing/'+niveau.code+'.csv'
    f=open(filename,'w')
    csvw=csv.writer(f)
    ue_list=Examen.objects.filter(Q(anuniv=curau) & Q(niveau=niveau)).order_by('ue').distinct('ue').values('ue')
    ue_listx=Examen.objects.filter(Q(anuniv=curau) & Q(niveau=niveau)).order_by('ue').distinct('ue').values('ue__ueid')
    ues=Examen.objects.filter(Q(anuniv=curau) & Q(niveau=niveau)).order_by('ue').distinct('ue')
    ueniv=Ue.objects.filter(ueid__in=ue_listx).order_by('semestre','biguecat')
    entete_seme=['','','']
    entete_ue=['','','']
    for e in ueniv:
        entete_seme.append(e.semestre)
        entete_ue.append(e.biguecat.categorie)
        entete.append(e.code)
    entete.append("CREDITS")
    entete.append("NBAN")
    entete.append("RESULTATS")
    tmp=Notes_Ue.objects.filter(examen__in=ues).distinct('etudiant').values_list('etudiant')
    etudiant_list=Etudiant.objects.filter(Q(etudiantid__in=tmp) & Q(cfc=False)).order_by('nompren')
    j=1
    data=[]
    csvw.writerow(entete_seme)
    csvw.writerow(entete_ue)
    csvw.writerow(entete)
    for et in etudiant_list:
        line=[]
        line.append(j)
        line.append(et.nce)
        line.append(et.nompren)
        for uex in ueniv:   
            admis=Resultat_info.objects.get(id=1)
            compense=Resultat_info.objects.get(id=2)
            ajourne=Resultat_info.objects.get(id=3)
            
            try: 
                n=get_object_or_404(Notes_Ue, Q(examen__ue=uex) & Q(etudiant=et) & (Q(resultat=admis)|Q(resultat=compense)))
                if n.resultat.id==1:
                    line.append(n.moyenne)
                if n.resultat.id==2:
                    line.append(str(n.moyenne)+'*')
            except:
                nadmis=Notes_Ue.objects.filter(Q(examen__ue=uex) & Q(etudiant=et) & (Q(resultat=admis)|Q(resultat=compense))).count()
            
                if nadmis>1:
                    line.append('A REVOIR')
                else:
                    try:
                        naj=get_object_or_404(Notes_Ue, Q(examen__ue=uex) & Q(etudiant=et) & Q(resultat=ajourne) & Q(examen__anuniv=curau) & Q(examen__session=2))
                        line.append(naj.moyenne)
                    except:
                        najc=Notes_Ue.objects.filter(Q(examen__ue=uex) & Q(etudiant=et) & Q(resultat=ajourne) & Q(examen__anuniv=curau) & Q(examen__session=2)).count()
                        if najc==0:
                        
                            try:
                                exa2=get_object_or_404(Examen,Q(niveau=niveau) & Q(ue=uex) & Q(anuniv=curau) & Q(session=2))
                                if uex.uelibre==False:
                                    
                                    line.append(0)
                                else:
                                    line.append('-')
                            except:
                      
                                try:
                                    eq=get_object_or_404(equivalence,Q(ue_from=uex))
                                    try:
                                        nadequi=get_object_or_404(Notes_Ue, Q(examen__ue=eq.ue_to) & Q(etudiant=et) & Q(resultat=admis))
                                        line.append(nadequi.moyenne)
                                    except:
                                        line.append('')
                                except:
                                    line.append('')
                   
            
        sumcredit=Notes_Ue.objects.values('etudiant').filter(Q(examen__niveau=niveau) & Q(resultat__id__lt=3) & Q(etudiant=et)).annotate(sumcredit=Sum('credits'))
        if sumcredit:
            line.append(sumcredit[0]['sumcredit'])
        else:
            line.append(0)
        try:
            resultat=get_object_or_404(Resultat,Q(niveau=niveau) & Q(etudiant=et) & Q(maxan=curau))
            line.append(resultat.nban)
            line.append(resultat.statut.labels)
        except:
            line.append('X')
            line.append('X')
        
        data.append(line)
        j=j+1
    csvw.writerows(data)
    f.close()
    return HttpResponseRedirect(reverse('vpv', args=[nivid,]))





def clean_notes_ue(request,nivid):
    #corriger_notes(nivid)
    #clean_notes_ue_ancien(nivid)
   
    recomp=Resultat_info.objects.get(id=6)
    admis=Resultat_info.objects.get(id=1)
    ajourne=Resultat_info.objects.get(id=3)
    niveau=Niveau.objects.get(nivid=nivid)
    curau=get_object_or_404(AnUniv,curau=True)
    notes=Notes_Ue.objects.filter(Q(resultat=recomp) & Q(examen__niveau=niveau)).values('etudiant','examen__ue')
    for n in notes:
        etudiant=Etudiant.objects.get(etudiantid=n['etudiant'])
        ue=Ue.objects.get(ueid=n['examen__ue'])
        n1=get_object_or_404(Notes_Ue, Q(etudiant=etudiant) & Q(examen__ue=ue) & Q(examen__session=1) & Q(examen__anuniv=curau))
        m1=n1.moyenne
   
        try:
            n2=get_object_or_404(Notes_Ue, Q(etudiant=etudiant) & Q(examen__ue=ue) & Q(examen__session=2) & Q(examen__anuniv=curau))
            m2=n2.moyenne
    
            if m1==m2 and n2.resultat==admis:
                n1.resultat=admis
                n1.save()
                n2.delete()
            if m2>m1 and n2.resultat==admis:
                n2.resultat=admis
                n2.save()
                n1.resultat=ajourne
                n1.save()
            if n1.resultat==etudiant_admisrecomp and n2.resultat==ajourne:
                n1.resultat=admis
                n1.save()
                n2.delete()
            if m2<m1 and n2.etudiant_admisresultat==admis:
                n1.resultat=admis
                n1.save()
                n2.delete()
        except:

            n1.resultat=admis
            n1.save()
    
        
    notes=Notes_Ue.objects.filter(Q(resultat=admis) & Q(examen__niveau=niveau)).values('etudiant','examen__ue')
    for n in notes:
        etudiant=Etudiant.objects.get(etudiantid=n['etudiant'])
        ue=Ue.objects.get(ueid=n['examen__ue'])
        try:

            n1=get_object_or_404(Notes_Ue, Q(etudiant=etudiant) & Q(examen__ue=ue) & Q(examen__session=1) & Q(examen__anuniv=curau) & Q(resultat=admis))
            m1=n1.moyenne
            try:
                n2=get_object_or_404(Notes_Ue, Q(etudiant=etudiant) & Q(examen__ue=ue) & Q(examen__session=2) & Q(examen__anuniv=curau) & Q(resultat=admis))
                m2=n2.moyenne
    
                if m1==m2 and n2.resultat==admis:
                    n1.resultat=admis
                    n1.save()
                    n2.delete()
                if m2>m1 and n2.resultat==admis:
                    n2.resultat=admis
                    n2.save()
                    n1.resultat=ajourne
                    n1.save()
                if m2<m1 and n2.resultat==admis:
                    n1.resultat=admis
                    n1.save()
                    n2.delete()
            except:
                pass
        except:
            pass
    
    #bigcat_resultat(nivid) 
  
    return HttpResponseRedirect(reverse('vpv', args=[nivid,]))

def clean_notes_ue_ancien(nivid):
    niveau=Niveau.objects.get(nivid=nivid)
    curau=get_object_or_404(AnUniv,curau=True)
    ajourne=Resultat_info.objects.get(id=3)
    admis=Resultat_info.objects.get(id=1)
    compense=Resultat_info.objects.get(id=2)
    exam_anc=Examen.objects.filter(Q(niveau=niveau) & Q(anuniv__lt=curau))
    for ex in exam_anc:
        etud_anc_admis=Notes_Ue.objects.filter(Q(examen=ex) & Q(resultat=admis)|Q(resultat=compense)).values('etudiant').distinct('etudiant')
        exam_nouv_list=Examen.objects.filter(Q(niveau=niveau) & Q(ue=ex.ue) & Q(anuniv=curau))
        note_nouv_aj=Notes_Ue.objects.filter(Q(etudiant__in=etud_anc_admis) & Q(examen__in=exam_nouv_list) & Q(resultat=ajourne))
        note_nouv_aj.delete()


def semestre_resultat(nivid):
    niveau=Niveau.objects.get(nivid=nivid)
    curau=get_object_or_404(AnUniv, curau=True)
    examen_list=Examen.objects.filter(Q(anuniv=curau) & Q(niveau=niveau))
    sem=Examen.objects.filter(Q(niveau=niveau) & Q(anuniv=curau)).distinct('ue__semestre').values_list('ue__semestre')
    etudiant_list=Notes_Ue.objects.filter(examen__in=examen_list).values('etudiant').distinct('etudiant')
    for s in sem:
        uelist=Examen.objects.filter(Q(niveau=niveau) & Q(anuniv=curau) & Q(ue__semestre=s[0])).distinct('ue').values('ue__ueid')
        coefsem=Ue.objects.filter(Q(niveau=niveau) & Q(ueid__in=uelist)).aggregate(sumcredit=Sum('credits'))
        coef=coefsem['sumcredit']
        moyenne=Notes_Ue.objects.values('etudiant','examen__ue__niveau','examen__ue__semestre').filter(Q(etudiant__in=etudiant_list) & Q(resultat__id__lte=2) & Q(examen__ue__semestre=s[0])).annotate(summoy=Sum('moypond'),sumcredit=Sum('examen__ue__credits'))
        for m in moyenne:
            obj,created=Resultat_semestre.objects.update_or_create(
                    etudiant=Etudiant.objects.get(etudiantid=m['etudiant']),
                    anuniv=curau,
                    niveau=niveau,
                    semestre=s[0],
                    defaults={'moyenne':m['summoy']/coef,'sumcredit':m['sumcredit']}
                )




def bigcat_resultat(request,nivid): 
    niveau=Niveau.objects.get(nivid=nivid)
    ajourne=Resultat_info.objects.get(id=3)
    curau=get_object_or_404(AnUniv, curau=True)
    examen_list=Examen.objects.filter(Q(anuniv=curau) & Q(niveau=niveau))
    raw_query= "update notes_ue set credits=a.credits from (select ue_id,id,credits from examens,ues where ue_id=ueid and anuniv_id>=1516) as a where examen_id=a.id"
    cursor=connection.cursor()
    cursor.execute(raw_query)
    Notes_Ue.objects.filter(examen__niveau=niveau).update(moypond=F('moyenne')*F('credits'))
    sem=Examen.objects.filter(Q(niveau=niveau) & Q(anuniv=curau)).distinct('ue__semestre').values_list('ue__semestre')
    etudiant_list=Notes_Ue.objects.filter(examen__in=examen_list).values('etudiant').distinct('etudiant')
    for s in sem:
        bigcat=Examen.objects.filter(Q(niveau=niveau) & Q(anuniv=curau) & Q(ue__semestre=s[0])).distinct('ue__biguecat').values_list('ue__biguecat')
        for b in bigcat:
            bc=BigUeCat.objects.get(bcid=b[0])
            uelist=Examen.objects.filter(Q(niveau=niveau) & Q(anuniv=curau) & Q(ue__semestre=s[0]) & Q(ue__biguecat=bc)).distinct('ue').values('ue__ueid')
            uelistx=Examen.objects.filter(Q(niveau=niveau) & Q(anuniv=curau) & Q(ue__semestre=s[0]) & Q(ue__biguecat=bc)).distinct('ue')
            ueuel=Examen.objects.filter(Q(niveau=niveau) & Q(anuniv=curau) & Q(ue__semestre=s[0]) & Q(ue__biguecat=bc) & Q(ue__uelibre=True)).distinct('ue').count()
            coefsem=Ue.objects.filter(Q(niveau=niveau) & Q(ueid__in=uelist)).aggregate(sumcredit=Sum('credits'))
            coefuel=Ue.objects.filter(Q(niveau=niveau) & Q(ueid__in=uelist) & Q(uelibre=True)).aggregate(sumcredit=Sum('credits'))
            if ueuel==2:
                coefx=coefuel['sumcredit']/2
                coef=coefsem['sumcredit']-coefx
            else:
                coef=coefsem['sumcredit']
            notes_ses1=Notes_Ue.objects.filter(Q(etudiant__in=etudiant_list) & Q(examen__ue__semestre=s[0]) & Q(examen__ue__biguecat=bc) & Q(examen__niveau=niveau) & Q(examen__session=1) & Q(resultat=ajourne)).values('id')
            notes_anc_aj=Notes_Ue.objects.filter(Q(etudiant__in=etudiant_list) & Q(examen__ue__semestre=s[0]) & Q(examen__ue__biguecat=bc) & Q(examen__niveau=niveau) & Q(examen__anuniv__lt=curau) & Q(resultat=ajourne)).values('id')
            moyenne=Notes_Ue.objects.values('etudiant','examen__ue__niveau','examen__ue__semestre','examen__ue__biguecat').filter(Q(etudiant__in=etudiant_list) & Q(examen__ue__semestre=s[0]) & Q(examen__ue__biguecat=bc) & Q(examen__niveau=niveau)).exclude(id__in=notes_ses1).exclude(id__in=notes_anc_aj).annotate(summoy=Sum('moypond'),sumcredit=Sum('examen__ue__credits'))

            for m in moyenne:
                etudiant=Etudiant.objects.get(etudiantid=m['etudiant'])
                ajourne=Resultat_info.objects.get(id=3)
                admis=Resultat_info.objects.get(id=1)
                ueval=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(examen__ue__biguecat=bc) & Q(resultat=admis) & Q(examen__ue__semestre=s[0])).values('examen__ue')
                nbueaj=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(examen__ue__biguecat=bc) & Q(resultat=ajourne) & Q(examen__ue__semestre=s[0])).exclude(examen__ue__in=ueval).distinct('examen__ue').count()
                nbue7=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(examen__ue__biguecat=bc) & Q(resultat=ajourne) & Q(examen__ue__semestre=s[0]) & Q(moyenne__lt=7) & Q(examen__session=2)).exclude(examen__ue__in=ueval).distinct('examen__ue').count()
                obj,created=Resultat_bigcat.objects.update_or_create(
                    etudiant=etudiant,
                    anuniv=curau,
                    niveau=niveau,
                    semestre=s[0],
                    biguecat=bc,
                    defaults={'moyenne':m['summoy']/coef,'credit':m['sumcredit'],'nbueaj':nbueaj,'somme':m['summoy'],'nbue7':nbue7}
                )
    semestre_resultat(nivid) 
    compensation(nivid) 
    return HttpResponseRedirect(reverse('vpv', args=[nivid,]))

def notes_ue_moypond_clean(nivid):
    niveau=Niveau.objects.get(nivid=nivid)
    curau=get_object_or_404(AnUniv, curau=True)
    examen_list=Examen.objects.filter(Q(anuniv=curau) & Q(niveau=niveau))
    for e in examen_list:
        notes=Notes_Ue.objects.filter(examen=e)
        for n in notes:
            n.save()


def set_exclus(nivid):
    pass
 
        


    

def set_stat(nivid,complet):
    niveau=Niveau.objects.get(nivid=nivid)
    curau=get_object_or_404(AnUniv, curau=True)
    examen_list=Examen.objects.filter(Q(anuniv=curau) & Q(niveau=niveau))
    sem=Examen.objects.filter(Q(niveau=niveau) & Q(anuniv=curau)).distinct('ue__semestre').values_list('ue__semestre')
    if complet==True:
        etudiant_list=Notes_Ue.objects.filter(examen__in=examen_list).values_list('etudiant').distinct('etudiant')
    else:
        etudiant_list=Notes_Ue.objects.filter(Q(examen__in=examen_list) & Q(decompense=True)).values_list('etudiant').distinct('etudiant')
    for et in etudiant_list:
        etudiant=Etudiant.objects.get(etudiantid=et[0])
        nban=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau)).distinct('examen__anuniv').count()
        sumcredit=Notes_Ue.objects.values('etudiant').filter(Q(examen__niveau=niveau) & Q(resultat__id__lt=3) & Q(etudiant=et)).annotate(sumcredit=Sum('credits'),sumoy=Sum('moypond'))
        try:
            credit=sumcredit[0]['sumcredit']
            moyenne=sumcredit[0]['sumoy']/credit
        except:
            credit=0
        maxan=curau
        admis=Statut_info.objects.get(id=1)
        cond=Statut_info.objects.get(id=2)
        redblt=Statut_info.objects.get(id=3)
        exclu=Statut_info.objects.get(id=4)
        impos=Statut_info.objects.get(id=5)
 
        if nban==1 and credit<48:
            statut=redblt
        if credit==60:
            statut=admis
        if nban==1 and credit>=48 and credit<60 and niveau.grade=='L' and niveau.nivgrade<3:
            statut=cond
        if nban==1 and credit>=48 and credit<60 and niveau.grade=='L' and niveau.nivgrade==3:
            statut=redblt
        if nban==1 and credit>=48 and credit<60 and niveau.grade=='M' and niveau.nivgrade<5:
            statut=cond
        if nban==1 and credit>=48 and credit<60 and niveau.grade=='M' and niveau.nivgrade==5:
            statut=redblt
        if nban>1 and credit<60:
            statut=exclu
        if nban>1 and credit>=48 and credit<60 and etudiant.epss==True and niveau.nivid==11:
            statut=cond
        if credit>60:
            statut=impos
        rescount=Resultat.objects.filter(Q(etudiant=etudiant) & Q(niveau=niveau) & Q(maxan=curau)).count()
        if rescount>1:
            res=Resultat.objects.filter(Q(etudiant=etudiant) & Q(niveau=niveau) & Q(maxan=curau))
            res.delete()
        
        obj,created=Resultat.objects.update_or_create(
                    etudiant=etudiant,
                    maxan=curau,
                    niveau=niveau,
                    defaults={'credit':credit,'nban':nban,'statut':statut,'moyenne':moyenne}
                )
    set_exclus(nivid)  

    
      


def compensation(nivid):
    niveau=Niveau.objects.get(nivid=nivid)
    #etudcomp=Resultat_bigcat.objects.filter(Q(niveau=niveau) & Q(nbueaj=1) &Q(moyenne__gte=10) & Q(nbue7=0))
    etudcomp=Resultat_bigcat.objects.filter(Q(niveau=niveau) & Q(nbueaj=1) &Q(moyenne__gte=10))
    ajourne=Resultat_info.objects.get(id=3)
    compense=Resultat_info.objects.get(id=2)
    curau=get_object_or_404(AnUniv, curau=True)
   
    Notes_Ue.objects.filter(Q(examen__niveau=niveau) & Q(examen__anuniv=curau) & Q(resultat=compense)).update(resultat=ajourne)
    for et in etudcomp:
        try:
            note_comp=get_object_or_404(Notes_Ue, Q(examen__niveau=niveau) & Q(examen__ue__biguecat=et.biguecat) &Q(etudiant=et.etudiant) & Q(resultat=ajourne) & Q(examen__session=2) & Q(moyenne__gte=7) & Q(examen__ue__semestre=et.semestre) & Q(examen__anuniv=curau))
            try:
                note_comp.resultat=compense
                note_comp.save()
            except:
                pass
        except:
            pass
    etudcomp=Resultat_bigcat.objects.filter(Q(niveau=niveau) & Q(nbueaj__gt=1) &Q(moyenne__gte=10))
    for et in etudcomp:
        max_note=Notes_Ue.objects.filter(Q(examen__niveau=niveau) & Q(examen__ue__biguecat=et.biguecat) &Q(etudiant=et.etudiant) & Q(resultat=ajourne) & Q(examen__session=2) & Q(moyenne__gte=7) & Q(examen__ue__semestre=et.semestre) & Q(examen__anuniv=curau)).aggregate(max_n=Max('moyenne'))
        maxnote=max_note['max_n']
        try:
            note_comp=get_object_or_404(Notes_Ue, Q(examen__niveau=niveau) & Q(examen__ue__biguecat=et.biguecat) &Q(etudiant=et.etudiant) & Q(resultat=ajourne) & Q(examen__session=2) & Q(moyenne=maxnote) & Q(examen__ue__semestre=et.semestre) & Q(examen__anuniv=curau))
            try:
                note_comp.resultat=compense
                note_comp.save()
            except:
                pass
        except:
            pass
    redblt=Statut_info.objects.get(id=3)
    exclu=Statut_info.objects.get(id=4)
    set_stat(nivid,True)
    etudxx=Resultat_bigcat.objects.filter(Q(niveau=niveau) & Q(nbueaj=1) &Q(moyenne__gte=10)).values('etudiant')
    etudiant_exclu=Resultat.objects.filter(Q(niveau=niveau) & Q(statut=exclu)|Q(statut=redblt) & Q(etudiant__in=etudxx)).values('etudiant')
    #Notes_Ue.objects.filter(Q(resultat=compense) & Q(etudiant__in=etudiant_exclu) & Q(examen__niveau=niveau) & Q(examen__anuniv=curau)).update(decompense=False)
    #Notes_Ue.objects.filter(Q(resultat=compense) & Q(etudiant__in=etudiant_exclu) & Q(examen__niveau=niveau) & Q(examen__anuniv=curau)).update(resultat=ajourne)
    
    

    set_stat(nivid,False)








def update_res_releve(nivid,etudiantid):
    niveau=Niveau.objects.get(nivid=nivid)
    etudiant=Etudiant.objects.get(etudiantid=etudiantid)
    nban=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau)).distinct('examen__anuniv').count()
    sumcredit=Notes_Ue.objects.values('etudiant').filter(Q(examen__niveau=niveau) & Q(resultat__id__lt=3) & Q(etudiant=etudiantid)).annotate(sumcredit=Sum('credits'),sumoy=Sum('moypond'))
    try:
        credit=sumcredit[0]['sumcredit']
        moyenne=sumcredit[0]['sumoy']/credit
    except:
            credit=0
    maxan=Notes_Ue.objects.values('etudiant').filter(Q(examen__niveau=niveau) & Q(resultat__id__lt=3) & Q(etudiant=etudiantid)).aggregate(maxan=Max('examen__anuniv'))
    
    ma=AnUniv.objects.get(auid=maxan['maxan'])
    
    admis=Statut_info.objects.get(id=1)
    cond=Statut_info.objects.get(id=2)
    redblt=Statut_info.objects.get(id=3)
    exclu=Statut_info.objects.get(id=4)
    impos=Statut_info.objects.get(id=5)
    if nban==1 and credit<48:
        statut=redblt
    if credit==60:
        statut=admis
    if nban==1 and credit>=48 and credit<60 and niveau.grade=='L' and niveau.nivgrade<3:
        statut=cond
    if nban==1 and credit>=48 and credit<60 and niveau.grade=='L' and niveau.nivgrade==3:
        statut=redblt
    if nban==1 and credit>=48 and credit<60 and niveau.grade=='M' and niveau.nivgrade<5:
        statut=cond
    if nban==1 and credit>=48 and credit<60 and niveau.grade=='M' and niveau.nivgrade==5:
        statut=redblt
    if nban>1 and credit<60:
        statut=exclu
    if nban>1 and credit>=48 and credit<60 and etudiant.epss==True and niveau.nivid==11:
        statut=cond
    if credit>60:
        statut=impos 
    obj,created=Resultat.objects.update_or_create(
                    etudiant=etudiant,
                    maxan=ma,
                    niveau=niveau,
                    defaults={'credit':credit,'nban':nban,'statut':statut,'moyenne':moyenne}
                )


class delete_note_ue(DeleteView):
    model=Notes_Ue
    slug_field='id'
    def get_success_url(self):
        niveau=self.object.examen.niveau
        etudiant=self.object.etudiant.etudiantid
        return reverse_lazy( 'releve', kwargs={'etudiantid':etudiant,'niveauid': niveau.nivid})


def corriger_notes(nivid):
    curau=get_object_or_404(AnUniv,curau=True)
    niveau=Niveau.objects.get(nivid=nivid)
    ue_listx=Examen.objects.filter(Q(anuniv=curau) & Q(niveau=niveau)).order_by('ue').distinct('ue').values('ue__ueid')
    ues=Examen.objects.filter(Q(anuniv=curau) & Q(niveau=niveau)).order_by('ue').distinct('ue')
    ueniv=Ue.objects.filter(ueid__in=ue_listx)    
    tmp=Notes_Ue.objects.filter(examen__in=ues).distinct('etudiant').values_list('etudiant')
    etudiant_list=Etudiant.objects.filter(etudiantid__in=tmp).order_by('nompren')
    for et in etudiant_list:
        for uex in ueniv:   
            admis=Resultat_info.objects.get(id=1)
            compense=Resultat_info.objects.get(id=2)
            ajourne=Resultat_info.objects.get(id=3)
            try:
                n=get_object_or_404(Notes_Ue, Q(examen__ue=uex) & Q(etudiant=et) & (Q(resultat=admis)|Q(resultat=compense)))
            except:
                pass
         

            
def gerer_compensation(request,examid):
    examen=get_object_or_404(Examen,Q(id=examid))
    ajourne=Resultat_info.objects.get(id=3)
    compense=Resultat_info.objects.get(id=2)
    curau=get_object_or_404(AnUniv, curau=True)
    candidat=Resultat_bigcat.objects.filter(Q(niveau=examen.niveau) & Q(semestre=examen.ue.semestre) & Q(biguecat=examen.ue.biguecat) & Q(moyenne__gte=10)).values('etudiant')
    deja_comp=Notes_Ue.objects.filter(Q(examen__niveau=examen.niveau) & Q(examen__ue__semestre=examen.ue.semestre) & Q(examen__ue__biguecat=examen.ue.biguecat) & Q(resultat=compense) & Q(examen__anuniv=curau)).values('etudiant')
    notes=Notes_Ue.objects.filter(Q(examen=examen) & Q(resultat=ajourne) & Q(moyenne__gte=7) & Q(etudiant__in=candidat)).exclude(etudiant__in=deja_comp).order_by('etudiant__nompren')
    context={}
    context['notes']=notes
    
    return  render(request,'notes3/gestion_compensation.html',context)

def check_ue_ajourne(request,nivid,semestre,etudiantid):
    etudiant=Etudiant.objects.get(etudiantid=etudiantid)
    niveau=Niveau.objects.get(nivid=nivid)
    ajourne=Resultat_info.objects.get(id=3)
    notes=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(examen__ue__semestre=semestre) & Q(resultat=ajourne) & Q(examen__session=2))
    context={}
    context['notes']=notes
    context['etudiant']=etudiant
    return  render(request,'notes3/releve_ajourne.html',context)


def detail_calcul(request,etudiantid,semestre,nivid,bcid):
    ajourne=Resultat_info.objects.get(id=3)
    etudiant=Etudiant.objects.get(etudiantid=etudiantid)
    niveau=Niveau.objects.get(nivid=nivid)
    biguecat=BigUeCat.objects.get(bcid=bcid)
    curau=get_object_or_404(AnUniv, curau=True)
    notes_ses1=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__ue__semestre=semestre) & Q(examen__ue__biguecat=biguecat) & Q(examen__niveau=niveau) & Q(examen__session=1) & Q(resultat=ajourne)).values('id')
    notes_anc_aj=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__ue__semestre=semestre) & Q(examen__ue__biguecat=biguecat) & Q(examen__niveau=niveau) & Q(examen__anuniv__lt=curau) & Q(resultat=ajourne)).values('id')
    notes=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__ue__semestre=semestre) & Q(examen__ue__biguecat=biguecat) & Q(examen__niveau=niveau)).exclude(id__in=notes_ses1).exclude(id__in=notes_anc_aj)
    context={}
    context['notes']=notes
  
    return  render(request,'notes3/detail_calcul.html',context)


def prtReleveNiv(request, niveauid):

    niveau=Niveau.objects.get(nivid=niveauid)
    semestre=Ue.objects.filter(niveau=niveau).distinct('semestre').order_by('semestre').values('semestre') 
    buffer = io.BytesIO()
    response = HttpResponse(content_type = 'application/pdf')
    response['Content-Disposition'] = 'inline; filename = "'+niveau.code+'.pdf"'
    doc = SimpleDocTemplate(buffer,   pagesizes = A4)
    story = []
    styles = getSampleStyleSheet()
    admis=Statut_info.objects.get(id=1)
    curau=get_object_or_404(AnUniv, curau=True)
    spnb1 = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 8,  
              fontName = "Times-Roman")
    splab = ParagraphStyle('parrafos',   
              alignment = TA_LEFT,  
              fontSize = 8,  
              fontName = "Times-Roman")
    list_exclu=exclu=Resultat.objects.filter(statut=4).distinct('etudiant').values('etudiant')
    etudsdd=Etudiant.objects.filter(Q(ddnais=None) |Q(lnais=None))
    list_etud=Resultat.objects.filter(Q(maxan=curau) & Q(niveau=niveau) & Q(statut=admis)).exclude(etudiant__in=list_exclu).order_by('etudiant__nompren')
    list_etudiant=list_etud.exclude(etudiant__in=etudsdd)
    for et in list_etudiant:
        etudiant=et.etudiant
        semestre_resultat_etudiant(niveauid,etudiant.etudiantid)
        bigcat_resultat_etudiant(etudiant.etudiantid,niveauid)
        data=[]
        theader = ['Semestre',   'Catégorie',   'Intitulés',   'Notes',   'Crédits',   'Validées',   'Moy.',   'Mention']
        data.append(theader)
        for sem in semestre:
            uecats=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(examen__ue__semestre=sem['semestre'])).values('examen__ue__biguecat').distinct('examen__ue__biguecat').order_by('examen__ue__biguecat')
            for uec in uecats:
                notes=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(examen__ue__semestre=sem['semestre']) & Q(examen__ue__biguecat=uec['examen__ue__biguecat']) & Q(resultat__lt=3))
                line=[]
                nl=0
                moy_uec=Resultat_bigcat.objects.filter(Q(etudiant=etudiant) & Q(niveau=niveau) & Q(semestre=sem['semestre']) & Q(biguecat=uec['examen__ue__biguecat'])).values('moyenne')
            
                for note in notes:
                    s=translate_sem(note.examen.ue.semestre)
                    if nl==0:
                        line.append(s)
                    else:
                        line.append('')
                    if nl==0:
                        line.append(Paragraph(note.examen.ue.biguecat.categorie,splab))
                    else:
                        line.append('')
                    line.append(Paragraph(note.examen.ue.labels,splab))
                    if note.resultat.id==1:
                        line.append(note.moyenne)
                    if note.resultat.id==2:
                        text=str(note.moyenne)+'*'
                        line.append(text)
                    line.append(note.examen.ue.credits)
                    line.append(note.examen.anuniv.labels)
                    if nl==0:
                        line.append(moy_uec[0]['moyenne'])
                    else:
                        line.append('')
                    if nl==0:
                        line.append(get_mention(moy_uec[0]['moyenne']))
                    else:
                        line.append('')
                    data.append(line)
                    line=[]
                    nl=nl+1
            moy_sem=Resultat_semestre.objects.filter(Q(etudiant=etudiant) & Q(niveau=niveau) & Q(semestre=sem['semestre'])).values('moyenne')
            data.append(['Moyenne du semestre '+str(sem['semestre']),'','','','','',moy_sem[0]['moyenne'],get_mention(moy_sem[0]['moyenne'])])
        moy_an=Resultat.objects.filter(Q(etudiant=etudiant) & Q(niveau=niveau)).values('moyenne')
        data.append(['Moyenne du annuelle ','','','','','',round(moy_an[0]['moyenne'],2),get_mention(moy_an[0]['moyenne'])])   
        spx = ParagraphStyle('parrafos',   
              alignment = TA_CENTER,  
              fontSize = 14,  
              fontName = "Times-Roman",  
              leading = 50)
        spx2 = ParagraphStyle('parrafos',   
              alignment = TA_CENTER,  
              fontSize = 14,  
              fontName = "Times-Roman",  
              leading = 20)

        sp = ParagraphStyle('parrafos',   
              alignment = TA_LEFT,  
              fontSize = 10,  
              fontName = "Times-Roman",
              leading = 20)
        
        spopt = ParagraphStyle('parrafos',   
              alignment = TA_CENTER,  
              fontSize = 10,  
              fontName = "Times-Roman",  
              leading = 20)
        x=Paragraph('.',spx)
        story.append(x)
        header = Paragraph("<b>Relevé de notes provisoire</b>",   spx2)
        story.append(header)
        fil = Filiere.objects.get(niveau = niveau)
        filp = Paragraph("<b>"+fil.specialite+"</b>",  spx2)
        story.append(filp)
        niv = Paragraph("<b>"+niveau.labels+"</b>",  spx2)
        story.append(niv)
        
        if niveau.option!=None:
            opt = Paragraph("<b>"+niveau.option+"</b>",  spopt)
            story.append(opt)
        nce = Paragraph("Numéro de carte d'étudiant: <b>"+etudiant.nce+"</b>",  sp )
        story.append(nce)
        nompren = Paragraph("Nom et prénoms: <b>"+etudiant.nom+" "+etudiant.prenoms+"</b>",   sp)
        story.append(nompren)
        dl = Paragraph("Date et lieu de naissance: <b>"+str(etudiant.ddnais.strftime("%d/%m/%y"))+"</b> à <b>"+etudiant.lnais+"</b>",   sp)
        story.append(dl)
        res=Resultat.objects.filter(Q(etudiant=etudiant) & Q(niveau=niveau)).values('nban')
        if res[0]['nban'] == 1:
            rdbl = Paragraph("Redoublant: <b>NON</b>",   sp)
        else:
            rdbl = Paragraph("Redoublant: <b>OUI</b>",   sp)
        story.append(rdbl)
        t = Table(data,   colWidths = [1.5*cm,   3.1*cm,   7.5*cm,   1.5*cm,   1.3*cm,   2*cm,   1.2*cm,  1.7*cm])
        stat=Notes_Ue.objects.values('examen__ue__semestre').annotate(nb=Count('examen__ue'))\
        .filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(resultat__lt=3))
    
        style=[]
        style.append(('GRID',  (0,  0),  (-1,  -1),  0.5,  colors.black))
        style.append(('FONTSIZE',   (0,   0),   (-1,   -1),   8))
        style.append(('VALIGN',   (0,   0),   (-1,   -1),   'MIDDLE'))
        style.append(('SPAN',   (0,    1),   (0,   stat[0]['nb']),))
        style.append(('SPAN',   (0,    stat[0]['nb']+2),   (0,   stat[0]['nb']+stat[1]['nb']+1),))
        style.append(('SPAN',   (0,    stat[0]['nb']+1),   (5,   stat[0]['nb']+1),))
        style.append(('SPAN',   (0,    stat[0]['nb']+stat[1]['nb']+2),   (5,   stat[0]['nb']+stat[1]['nb']+2),))
        style.append(('SPAN',   (0,    stat[0]['nb']+stat[1]['nb']+3),   (5,   stat[0]['nb']+stat[1]['nb']+3),))
        sem=Notes_Ue.objects.values('examen__ue__semestre').annotate(nb=Count('examen__ue'))\
        .filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(resultat__lt=3))
        col=[1,6,7]
   
    
        for c in  col:
            srow=1
            erow=0   
            for s in sem:
                ustat=Notes_Ue.objects.values('examen__ue__biguecat').annotate(nb=Count('examen__ue'))\
                .filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(resultat__lt=3) & Q(examen__ue__semestre=s['examen__ue__semestre'])).order_by('examen__ue__biguecat')
                for u in ustat:
                    if u['nb']==1:
                        srow=srow+u['nb']
                    if u['nb']>1:
                        erow=srow+u['nb']-1
                        style.append(('SPAN',   (c,    srow),   (c,   erow),))
                        srow=erow+1
                srow=srow+1
    
   
        t.setStyle(TableStyle(style))
        story.append(t)
        spd = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 12,  
              fontName = "Times-Roman",  
              leading = 40)
        spn = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 12,  
              fontName = "Times-Roman")
        spnb1 = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 8,  
              fontName = "Times-Roman")
        spnb2 = ParagraphStyle('parrafos',   
              alignment = TA_RIGHT,  
              fontSize = 8,  
              fontName = "Times-Roman",  
              leading = 10)
        spass = ParagraphStyle('parrafos',   
              alignment = TA_LEFT,  
              fontSize = 10,  
              fontName = "Times-Roman",  
              leading = 10)
        nb = Paragraph("Les moyennes accompagnées de * ont été compensées",   spnb1)
        story.append(nb)
        nb = Paragraph("Valable 3 mois à compter de sa date de signature",   spnb2)
        story.append(nb)
        if niveau.nivto==None:
            pass
        else:
            nb = Paragraph("Admis(e) en <b>"+niveau.nivto+"</b>",   spass)
            story.append(nb)
        ledoyen = Paragraph('<b>Le Directeur</b>',   spd)
        story.append(ledoyen)
        nomdoyen = Paragraph('<b>TIHO Séydou</b>',   spn) 
        story.append(nomdoyen)
        story.append(PageBreak())
        
    filp = Paragraph("<b>Liste d'émargement</b>",  spx2)
    story.append(filp) 
    style=[]
    style.append(('GRID',  (0,  0),  (-1,  -1),  0.5,  colors.black))
    style.append(('FONTSIZE',   (0,   0),   (-1,   -1),   8))
    data=[]
    theader = ['Num.','NCE','Nom et prénoms','Date de retrait', 'Emargement']
    data.append(theader)
    list_exclu=exclu=Resultat.objects.filter(statut=4).distinct('etudiant').values('etudiant')
    list_etudiant=Resultat.objects.filter(Q(maxan=curau) & Q(niveau=niveau) & Q(statut=admis)).exclude(etudiant__in=list_exclu).order_by('etudiant__nompren')
    j=1
    for et in list_etudiant:
        etudiant=et.etudiant
        line=[]
        line.append(j)
        line.append(et.etudiant.nce)
        line.append(et.etudiant.nompren)
        line.append('')
        line.append('')
        data.append(line)
        j=j+1
    t = Table(data,   colWidths = [1*cm, 3*cm,  7.5*cm,   4*cm,   5*cm])
    t.setStyle(TableStyle(style))
    story.append(t)
    doc.build(story)
        
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
def clean_resultat(nivid):
    resdblt=Resultat.objects



class resultat_delete(DeleteView):
    model=Resultat
    slug_field='id'
    def get_success_url(self, **kwargs):
        etudiantid=self.object.etudiant.etudiantid
        return reverse_lazy('resultats', args=(etudiantid,))


def get_uex_list(request):
    niveau_id=request.GET.get("niveau_id")
    niveau=Niveau.objects.get(nivid=niveau_id)
    context={}
    context['ues']=Ue.objects.filter(niveau=niveau)
    return render(request,'notes3/uex.html',context)


def filiere_list(request):
    filiere=Filiere.objects.all()
    context={}
    context['filiere']=filiere
    return render(request,'notes3/filiere_l.html',context)

def niveau_l(request):
    filid=request.GET.get('filid')
    fil=Filiere.objects.get(filid=filid)
    niveaux=Niveau.objects.filter(filiere=fil).order_by('labels')
    context={}
    context['niveaux']=niveaux
    return render(request,'notes3/niveau_l.html',context)


def niveau_l2(request):
    anuniv=get_object_or_404(AnUniv,Q(curau=True))
    niveaux=Niveau.objects.filter(filiere__anuniv=anuniv).order_by('labels')
    context={}
    context['niveaux']=niveaux
    return render(request,'notes3/niveau_l.html',context)

def examen_l(request):
    niveau_id=request.GET.get('niveau_id')
    niveau=Niveau.objects.get(nivid=niveau_id)
    examens=Examen.objects.filter(niveau=niveau).order_by('anuniv')
    context={}
    context['examens']=examens
    return render(request,'notes3/examen_l.html',context)
#Effacer une fois terminée

class notes_ue_etudiant(CreateView):
    model=Notes_Ue
    template_name='notes3/notes_ue_add.html'
    form_class=addnote
    def get_initial(self):
        initial=super(notes_ue_etudiant, self).get_initial()
        initial=initial.copy()
        initial['etudiant']=self.kwargs['etudiantid']
        return initial
    def get_success_url(self):
        etudiantid=self.kwargs['etudiantid']
        return reverse_lazy( 'ustudres', kwargs={'etudiant_id': etudiantid})



def update_res_stud(request,etudiant_id):
    etudiant=get_object_or_404(Etudiant,Q(etudiantid=etudiant_id))
    etres=Resultat.objects.filter(etudiant=etudiant).values('niveau')
    etres=Notes_Ue.objects.filter(etudiant=etudiant).distinct('examen__niveau').exclude(examen__niveau__in=etres).values('examen__niveau')
  
    for n in etres:
        update_res_releve(n['examen__niveau'],etudiant_id)

    return HttpResponseRedirect(reverse('resultats',args=(etudiant_id,)))

    
def semestre_resultat_etudiant(nivid,etudiantid):
    niveau=Niveau.objects.get(nivid=nivid)
    etudiant=get_object_or_404(Etudiant, etudiantid=etudiantid)
    sem=Notes_Ue.objects.filter(Q(examen__niveau=niveau) & Q(etudiant=etudiant)).distinct('examen__ue__semestre').values_list('examen__ue__semestre')

    for s in sem:
        uelist=Notes_Ue.objects.filter(Q(examen__niveau=niveau) & Q(examen__ue__semestre=s[0]) & Q(etudiant=etudiant)).distinct('examen__ue').values('examen__ue__ueid')
        coefsem=Ue.objects.filter(Q(niveau=niveau) & Q(ueid__in=uelist)).aggregate(sumcredit=Sum('credits'))
        coef=coefsem['sumcredit']
        print(coef)
        moyenne=Notes_Ue.objects.values('etudiant','examen__ue__niveau','examen__ue__semestre').filter(Q(etudiant=etudiant) & Q(resultat__id__lte=2) & Q(examen__ue__semestre=s[0])).annotate(summoy=Sum('moypond'),sumcredit=Sum('examen__ue__credits'))

        maxan=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(examen__ue__semestre=s[0])).aggregate(anuniv=Max('examen__anuniv'))
        for m in moyenne:
            print(m['summoy']/coef)
            obj,created=Resultat_semestre.objects.update_or_create(
                    etudiant=etudiant,
                    anuniv=AnUniv.objects.get(auid=maxan['anuniv']),
                    niveau=niveau,
                    semestre=s[0],
                    defaults={'moyenne':m['summoy']/coef,'sumcredit':m['sumcredit']}
                )
    
    bigcat_resultat_etudiant(etudiantid,nivid)
    update_res_releve(nivid,etudiantid)

def bigcat_resultat_etudiant(etudiantid,nivid): 
    niveau=Niveau.objects.get(nivid=nivid)
    ajourne=Resultat_info.objects.get(id=3)
    curau=get_object_or_404(AnUniv, curau=True)

    examen_list=Examen.objects.filter(Q(anuniv=curau) & Q(niveau=niveau))
    etudiant=get_object_or_404(Etudiant, etudiantid=etudiantid)
    sem=Ue.objects.filter(Q(niveau=niveau) ).distinct('semestre').values_list('semestre')
    r=Resultat_bigcat.objects.filter(Q(etudiant=etudiant) & Q(niveau=niveau))
    if r:
        r.delete()
    for s in sem:
        bigcat=Ue.objects.filter(Q(niveau=niveau)  & Q(semestre=s[0])).distinct('biguecat').values_list('biguecat')
        for b in bigcat:
            bc=BigUeCat.objects.get(bcid=b[0])
            uelist=Notes_Ue.objects.filter(Q(examen__niveau=niveau) & Q(etudiant=etudiant) & Q(examen__ue__semestre=s[0]) & Q(examen__ue__biguecat=bc)).distinct('examen__ue').values('examen__ue__ueid')
            uelistx=Notes_Ue.objects.filter(Q(examen__niveau=niveau) & Q(etudiant=etudiant) & Q(examen__ue__semestre=s[0]) & Q(examen__ue__biguecat=bc)).distinct('examen__ue')
            ueuel=Notes_Ue.objects.filter(Q(examen__niveau=niveau) & Q(etudiant=etudiant) & Q(examen__ue__semestre=s[0]) & Q(examen__ue__biguecat=bc) & Q(examen__ue__uelibre=True)).distinct('examen__ue').count()
            coefsem=Ue.objects.filter(Q(niveau=niveau) & Q(ueid__in=uelist)).aggregate(sumcredit=Sum('credits'))
            uex=Ue.objects.filter(Q(niveau=niveau) & Q(ueid__in=uelist)).distinct('ueid')
            coefuel=Ue.objects.filter(Q(niveau=niveau) & Q(ueid__in=uelist) & Q(uelibre=True)).aggregate(sumcredit=Sum('credits'))
            if ueuel==2:
                coefx=coefuel['sumcredit']/2
                coef=coefsem['sumcredit']-coefx
            else:
                coef=coefsem['sumcredit']
           
            notes_ses1=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__ue__in=uelist) & Q(examen__niveau=niveau) & Q(resultat__isnull=True)).values('id')
            notes_anc_aj=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__ue__semestre=s[0]) & Q(examen__ue__biguecat=bc) & Q(examen__niveau=niveau) & Q(examen__anuniv__lt=curau) & Q(resultat=ajourne)).values('id')

            moyenne=Notes_Ue.objects.values('etudiant','examen__ue__niveau','examen__ue__semestre','examen__ue__biguecat').filter(Q(etudiant=etudiant) & Q(examen__ue__in=uex) & Q(examen__niveau=niveau)).exclude(id__in=notes_ses1).exclude(id__in=notes_anc_aj).annotate(summoy=Sum('moypond'),sumcredit=Sum('examen__ue__credits'))
            nb=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__ue__in=uelist) & Q(examen__niveau=niveau)).exclude(id__in=notes_ses1).exclude(id__in=notes_anc_aj)
        
            
            for m in moyenne:
                ajourne=Resultat_info.objects.get(id=3)
                admis=Resultat_info.objects.get(id=1)
                ueval=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(examen__ue__biguecat=bc) & Q(resultat=admis) & Q(examen__ue__semestre=s[0])).values('examen__ue')
                nbueaj=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(examen__ue__biguecat=bc) & Q(resultat=ajourne) & Q(examen__ue__semestre=s[0])).exclude(examen__ue__in=ueval).distinct('examen__ue').count()
                nbue7=Notes_Ue.objects.filter(Q(etudiant=etudiant) & Q(examen__niveau=niveau) & Q(examen__ue__biguecat=bc) & Q(resultat=ajourne) & Q(examen__ue__semestre=s[0]) & Q(moyenne__lt=7) & Q(examen__session=2)).exclude(examen__ue__in=ueval).distinct('examen__ue').count()
                
                
                obj,created=Resultat_bigcat.objects.update_or_create(
                    etudiant=etudiant,
                    anuniv=curau,
                    niveau=niveau,
                    semestre=s[0],
                    biguecat=bc,
                    defaults={'moyenne':m['summoy']/coef,'credit':m['sumcredit'],'nbueaj':nbueaj,'somme':m['summoy'],'nbue7':nbue7}
                )

def update_examen_id(request,niveauid):
    niv=Niveau.objects.get(nivid=niveauid)
    exam_list=Examen.objects.filter(Q(id__lt=10000) & Q(niveau=niv))
    for e in exam_list:
        new_id=e.anuniv.auid*100000+e.ue.ueid*10+e.session
        obj,created=Examen.objects.update_or_create(
                    anuniv=e.anuniv,
                    niveau=e.niveau,
                    ue=e.ue,
                    session=e.session+2,
                    id=new_id,
                    defaults={'examdate':e.examdate,'delibdate':e.delibdate,'delib':e.delib,'calcul':e.calcul,'ecue_ignored':e.ecue_ignored,'afficher':e.afficher,'reporter':e.reporter}
                )
        new_examen=Examen.objects.get(id=new_id)
        Notes_Ue.objects.filter(examen=e).update(examen=new_examen)
        Composition.objects.filter(examen=e).update(examen=new_examen)
        Notes_ecue.objects.filter(examen=e).update(examen=new_examen)
        moyenne_ue_cmtp.objects.filter(examen=e).update(examen=new_examen)
        moyenne_ecue_tmp.objects.filter(examen=e).update(examen=new_examen)
        moyenne_ecue.objects.filter(examen=e).update(examen=new_examen)
        e.delete()
        new_examen.session=new_examen.session-2
        new_examen.save()
    return HttpResponse('Merci')


def update_xxx(request):
    niv=Niveau.objects.get(nivid=73)
    examens=Examen.objects.filter(niveau=niv)
    for e in examens:
        if e.id<10000:
            new_exams=Examen.objects.filter(Q(niveau=e.niveau) & Q(ue=e.ue) & Q(id__gt=10000))
            for ne in new_exams:
                Notes_Ue.objects.filter(examen=ne).update(examen=e)
                Composition.objects.filter(examen=ne).update(examen=e)
                Notes_ecue.objects.filter(examen=ne).update(examen=e)
                ne.delete()
    return HttpResponse('Merci')


def t_niveau(request):
    examenid=request.GET.get("examid")
    examen=Examen.objects.get(id=examenid)
    niveau=Niveau.objects.filter(Q(filiere=examen.niveau.filiere) & Q(nivgrade=examen.niveau.nivgrade)).exclude(nivid=examen.niveau.nivid)
    context={}
    context['niveaux']=niveau
    return render(request,'notes3/niveau_l.html',context)

def t_examen(request):
    examenid=request.GET.get("examid")
    nivid=request.GET.get("niveauid")
    niveau=Niveau.objects.get(nivid=nivid)
    examen=Examen.objects.get(id=examenid)
    ue=examen
    t_examen=Examen.objects.filter(Q(niveau=niveau) & Q(ue__code=examen.ue.code) & Q(session=examen.session) & Q(anuniv=examen.anuniv))
    context={}
    context['examens']=t_examen
    return render(request, 'notes3/tmp_examen_list.html' ,context)

def ex_recharger(request,examid):
    exam=Examen.objects.get(id=examid)
    exam.afficher=False
    exam.save()
    return HttpResponseRedirect(reverse('detexam',args=(examid,)))

def ano_generation(request,compoid):
    compo=Composition.objects.get(compid=compo_id)
    examen=compo.examen
    admis=Resultat_info.objects.get(id=1)

    if compo.ano==True :
        for et in list:
            print(et.nompren)

    return HttpResponse('Merci')


class AnUniv_create(CreateView):
    model=AnUniv
    template_name='notes3/anuniv_create.html'
    success_url=reverse_lazy('index')
    form_class=AnUnivform
    def get_initial(self):
        initial=super(AnUniv_create, self).get_initial()
        initial=initial.copy()
        max_id=AnUniv.objects.aggregate(max=Max('auid'))
        auid=max_id['max']+101
        initial['auid']=auid
        initial['lauid']=max_id['max']
        stran=str(2000+int(str(auid)[:-2])) +'-'+ str(2000+int(str(auid)[-2:]))
        initial['labels']=stran
        return initial



class anuniv_update(UpdateView):
    model=AnUniv
    slug_field='auid'
    fields=['finish','inscrit']
    template_name_suffix='_update_form'
    def get_success_url(self):
        return reverse('index')

def add_filiere(request,auid):
    an=AnUniv.objects.get(auid=auid)
    lanid=an.lauid
    lan=AnUniv.objects.get(auid=lanid)
    filieres=Filiere.objects.filter(anuniv=lan)
    for f in filieres:
        obj,created=Filiere.objects.update_or_create(
                    filid=f.filid-lanid+auid,
                    label=f.label,
                    domaine=f.domaine,
                    mention=f.mention,
                    specialite=f.specialite,
                    responsable=f.responsable,
                    anuniv=an,
                )
    return HttpResponseRedirect(reverse('filieres',args=(auid,)))


def add_niveaux(request,filid,auid):
    an=AnUniv.objects.get(auid=auid)
    lanid=an.lauid
    lan=AnUniv.objects.get(auid=lanid)
    filiere=Filiere.objects.get(filid=filid)
    filok=get_object_or_404(Filiere,Q(anuniv=lan) & Q(label=filiere.label))
    nivlist=Niveau.objects.filter(Q(filiere=filok))
    for n in nivlist:
        nivid=int(str(n.nivid)+str(auid)[-2:])
        obj,created=Niveau.objects.update_or_create(
                    nivid=nivid,
                    code=n.code,
                    labels=n.labels,
                    option=n.option,
                    grade=n.grade,
                    nivgrade=n.nivgrade,
                    nbres=n.nbres,
                    filiere=filiere,
                    responsable=n.responsable,
                    coeftp=n.coeftp,
                    coefcm=n.coefcm,
                    coeftd=n.coeftd,
                    conseiller=n.conseiller,
                    nivto=n.nivto,   
                )

    
    return HttpResponseRedirect(reverse('niveaux',args=(filid,)))


def add_ues(request,nivid):
    niveau=Niveau.objects.get(nivid=nivid)
    filiere=niveau.filiere
    an=filiere.anuniv
    lanid=an.lauid
    lan=AnUniv.objects.get(auid=lanid)
    filok=get_object_or_404(Filiere,Q(anuniv=lan) & Q(label=filiere.label))
    nivancien=get_object_or_404(Niveau,Q(filiere__anuniv=lan) & Q(code=niveau.code))
    ues=Ue.objects.filter(niveau=nivancien).order_by('semestre','labels',)
    j=1
    for  ue in ues:
        ueid=int(str(nivid)+str(ue.semestre)+str(ue.biguecat.bcid)+str(j))
        print(ueid)
        obj,created=Ue.objects.update_or_create(
            ueid = ueid,
            code = ue.code,
            labels = ue.labels,
            semestre = ue.semestre,
            credits = ue.credits,
            niveau = niveau,
            uecat = ue.uecat,
            inuse=ue.inuse,
            coefcm=ue.coefcm,
            coeftp=ue.coeftp,
            coeftd=ue.coeftd,
            biguecat=ue.biguecat,
            uelibre=ue.uelibre,
        )
        j=j+1
        ueis=UeInfo.objects.filter(ue=ue)
        uex=Ue.objects.get(ueid=ueid)
        i=1
        for uei in ueis:
            obj,created=UeInfo.objects.update_or_create(
                uei = int(str(uex.ueid)+str(i)),
                code = uei.code,
                labels = uei.labels,
                credits = uei.credits,
                ecue_ignored = uei.ecue_ignored,
                niveau = niveau,
                ue = uex,
                inuse=uei.inuse,
            )
            i=i+1

    return HttpResponseRedirect(reverse('listue',args=(nivid,)))



        
def openform_inscription(request,niveauid):
      niveau=Niveau.objects.get(nivid=niveauid)
      anuniv=niveau.filiere.anuniv
      context={
        'niveau':niveau.nivid,
        'anuniv':anuniv,
      }
      return render(request,'notes3/inscription_form.html',context)



def inscrire_auto(request,niveauid):
    niveau=Niveau.objects.get(nivid=niveauid)
    anuniv=niveau.filiere.anuniv
    lauid=anuniv.lauid
    lan=AnUniv.objects.get(auid=lauid)
    admis=Statut_info.objects.get(id=1)
    exclu=Statut_info.objects.get(id=4)
    redblt=Statut_info.objects.get(id=3)
    cond=Statut_info.objects.get(id=2)
    nivancien=get_object_or_404(Niveau,Q(filiere__anuniv=lan) & Q(code=niveau.code))
    nivfrom=Niveau_from_to.objects.filter(niveau=nivancien)
    
    for niv in nivfrom:
        et_exc=Resultat.objects.filter(Q(niveau=niv.niveaufrom) & Q(maxan=lan) & Q(statut=exclu)).values_list('etudiant')
        et_red=Resultat.objects.filter(Q(niveau=niv.niveaufrom) & Q(maxan=lan) & Q(statut=redblt)).values_list('etudiant')
        tmp=Resultat.objects.filter(Q(niveau=niv.niveaufrom) & Q(maxan=lan)).exclude(etudiant__in=et_exc).order_by('etudiant__nompren')
        et_list=tmp.exclude(etudiant__in=et_red)
    
    context={}
  
    nouveau=Statut_info.objects.get(id=6)
    n=tmp_inscr.objects.all()
    if n:
        n.delete()
    for et in et_list:
        obj,created=tmp_inscr.objects.update_or_create(
                                statut = nouveau,
                                nban = et.nban,
                                anuniv = anuniv,
                                etudiant = et.etudiant,
                                niveau = niveau,
                                )
    et_db=Resultat.objects.filter(Q(niveau=nivancien) & Q(statut=redblt) & Q(maxan=lan))

    for et in et_db:
        obj,created=tmp_inscr.objects.update_or_create(
                                statut = redblt,
                                nban = et.nban,
                                anuniv = anuniv,
                                etudiant = et.etudiant,
                                niveau = niveau,
                                )
    et_db=Resultat.objects.filter(Q(niveau=nivancien) & Q(statut=cond) & Q(maxan=lan))

    for et in et_db:
        obj,created=tmp_inscr.objects.update_or_create(
                                statut = cond,
                                nban = et.nban,
                                anuniv = anuniv,
                                etudiant = et.etudiant,
                                niveau = niveau,
                                )
    et_list=tmp_inscr.objects.all().order_by('etudiant__nompren')
    context['inscr']=et_list
    context['curau']=anuniv.auid
    context['niveau']=niveauid
    return render(request,'notes3/tmp_inscr.html',context)






def upload_inscription(request,niveauid):
    admis=Statut_info.objects.get(id=1)
    redblt=Statut_info.objects.get(id=3)
    cond=Statut_info.objects.get(id=2)
    exclu=Statut_info.objects.get(id=4)
    impos=Statut_info.objects.get(id=5)
    averif=Statut_info.objects.get(id=7)
    niveau=Niveau.objects.get(nivid=niveauid)
    if 'GET'==request.method:
        pass
    else:
            excel_file=request.FILES["excel_file"]
            data=get_data(excel_file)
            prefix=niveau.code
            sheet=data[prefix]
            anuniv=niveau.filiere.anuniv
            n=tmp_inscr.objects.all()
            if n:
                n.delete()
            n=err_inscription.objects.all()
            if n:
                n.delete()
            for row in sheet:
    
                if len(row)==0:
                            break
                if len(row[0].strip())<12:
                    pass
                else:
                    if len(row[0].strip())==12:
                        et=int(row[0][-8:].strip())
                        etudiant=get_object_or_404(Etudiant,Q(etudiantid=et))
                        exclu=Statut_info.objects.get(id=4)
                        stat=get_nivstat(et,niveau.filiere.anuniv.auid,niveau.nivid)
                        statut=Statut_info.objects.get(id=stat['statid'])
                        nban=stat['nban']
                        if (statut==impos) or (statut==averif):
                            e=err_inscription.objects.create(
                                statut = statut,
                                nban = nban,
                                anuniv = anuniv,
                                etudiant = etudiant,
                                niveau = niveau,
                                )
                            e.save()
                        else:
                            obj,created=tmp_inscr.objects.update_or_create(
                                statut = statut,
                                nban = nban,
                                anuniv = anuniv,
                                etudiant = etudiant,
                                niveau = niveau,
                                )
    context={}
    tmp=tmp_inscr.objects.all().order_by('etudiant__nompren')
    context['inscr']=tmp
    context['niveau']=niveau.nivid
    context['nombre']=tmp.count()
    return render(request, 'notes3/inscr_tmp.html', context)



def get_nivstat(etudiantid,auid,niveauid):
    etudiant=Etudiant.objects.get(etudiantid=etudiantid)
    anuniv=get_object_or_404(AnUniv,Q(auid=auid))
    niveau=Niveau.objects.get(nivid=niveauid)
    lan=get_object_or_404(AnUniv,Q(auid=anuniv.lauid))
    admis=Statut_info.objects.get(id=1)
    redblt=Statut_info.objects.get(id=3)
    cond=Statut_info.objects.get(id=2)
    exc=Statut_info.objects.get(id=4)
    impos=Statut_info.objects.get(id=5)
    exclu=Resultat.objects.filter(Q(etudiant=etudiant) & Q(statut=exc)).count()
    nivx=Niveau.objects.get(Q(code=niveau.code) & Q(filiere__anuniv=lan))
    rescount=Resultat.objects.filter(etudiant=etudiant).count()
    
    if rescount==0:
        statid=6
        nban=1
    else:
        try:
            resultat=Resultat.objects.get(Q(etudiant=etudiant) & Q(maxan=lan) & Q(niveau=nivx))
            if (resultat.statut==redblt) :
                statid=3
                nban=2
            if resultat.statut==exc:
                statid=4
                nban=resultat.nban
            if resultat.statut==impos:
                statid=5
                nban=resultat.nban
            if resultat.statut==cond:
                statid=6
                nban=1
            if resultat.statut==admis:
                statid=5
                nban=0
        except:
            try: 
                maxniv=Resultat.objects.filter(Q(etudiant=etudiant) & Q(maxan=lan) & Q(niveau__nivgrade=niveau.nivgrade-1)).aggregate(max=Max('niveau'))
                ancniveau=Niveau.objects.get(nivid=maxniv['max'])
                res=Resultat.objects.get(Q(etudiant=etudiant) & Q(maxan=lan) & Q(niveau=ancniveau))
                statid=7
                nban=1
                if res.statut==exc:
                    statid=4
                    nban=res.nban
                if res.statut==admis:
                    statid=6
                    nban=1
                if res.statut==cond:
                    statid=6
                    nban=1
                if res.statut==redblt:
                    statid=5
                    nban=1
            except:
                statid=7
                nban=1
    statut={}     
    statut['statid']=statid
    statut['nban']=nban
    return statut


def inscrire(request,niveauid):
    inscrs=tmp_inscr.objects.all()
    for i in inscrs:
        try:
            i=Inscription.objects.update_or_create(
                                statut = i.statut,
                                nban = i.nban,
                                niveau=i.niveau,
                                anuniv=i.anuniv,
                                etudiant=i.etudiant,
            )
            i.save()
        except:
            pass
    niveau=Niveau.objects.get(nivid=niveauid)
    anuniv=niveau.filiere.anuniv
    nombre=Inscription.objects.filter(Q(niveau=niveau) & Q(anuniv=anuniv)).count()
    niveau.effectif=nombre
    niveau.save()
    return HttpResponseRedirect(reverse('rinscrire',args=(niveauid,)))



def inscript_report(request,niveauid):
    admis=Statut_info.objects.get(id=1)
    redblt=Statut_info.objects.get(id=3)
    cond=Statut_info.objects.get(id=2)
    exclu=Statut_info.objects.get(id=4)
    impos=Statut_info.objects.get(id=5)
    averif=Statut_info.objects.get(id=7)
    niveau=Niveau.objects.get(nivid=niveauid)
    anuniv=niveau.filiere.anuniv
    nombre=Inscription.objects.filter(Q(niveau=niveau) & Q(anuniv=anuniv)).count()
    error=err_inscription.objects.filter(Q(niveau=niveau) & Q(anuniv=anuniv))
    if error.count()==0:
        text="Tous les étudiants de la liste ont été incorporés dans la base de données"
    elif error.count()>0:
        text="Au titre de l'année 2018-2019, "+str(nombre)+" étudiants on été incorporés. cependant les etudiants dont les noms suivent, outre les étudiants non encore insscrits à l'UNA:\n"
        for e in error:
            if e.statut==impos:
                text=text+"\t"+"-"+e.etudiant.nompren+"("+e.etudiant.nce+") est admis en année supérieure.\n"
            if e.statut==exclu:
                text=text+"\t"+"-"+e.etudiant.nompren+"("+e.etudiant.nce+") est exclu des effectifs\n."
            if e.statut==averif:
                text=text+"\t"+"-"+e.etudiant.nompren+"("+e.etudiant.nce+") possède des données incomplètes\n."
    text=text+"\n"+"Ce message est automatiquement généré par le sustème"
    to_list=['danhofr@gmail.com','setiho@hotmail.com','eloik@yahoo.fr','ahuerod.inf@univ-na.ci ']
    email=niveau.responsable
    message=text
    sujet="Rapport de l'incorporation de la liste des étudiants  dans la base de données en " +niveau.code +"("+ anuniv.labels +") sous reserve de l'inscription"
    if email==None:
        pass
    else:
        to_list.append(email)
    email=EmailMessage(sujet,
        message,
        to=to_list
    )
    email.send()
    return HttpResponseRedirect(reverse('niveaux',args=(niveau.filiere.filid,)))

def check_epss():
    etepss=Etudiant.objects.filter(epss=True).values_list('etudiantid')
    nouveau=Statut_info.objects.get(id=6)
    redoublant=Statut_info.objects.get(id=3)
    insepss=Inscription.objects.filter(Q(etudiant__in=etepss) & Q(statut=nouveau))
    for i in insepss:
        i.statut=redoublant
        i.nban=2
        i.save()


def inscrit_list(request,niveauid):
    niveau=Niveau.objects.get(nivid=niveauid)
    anuniv=niveau.filiere.anuniv
    inscrit=Inscription.objects.filter(Q(niveau=niveau) & Q(anuniv=anuniv)).order_by('etudiant__nompren')
    if niveauid==1119:
        check_epss()
    context={}
    context['inscr']=inscrit
    context['nivid']=niveau.nivid
    context['niveau']=niveau
    context['curau']=anuniv.auid
    context['nombre']=inscrit.count()
    context['scolarite']=anuniv.inscrit
    return render(request, 'notes3/inscrip_list.html', context)


def get_etstat(request):
    etudiantid=request.GET.get('etudiantid')
    niveauid=request.GET.get('niveauid')
    niveau=Niveau.objects.get(nivid=niveauid)
    anuniv=niveau.filiere.anuniv
    lauid=anuniv.lauid
    lan=AnUniv.objects.get(auid=lauid)
    anfil=get_object_or_404(Filiere,Q(label=niveau.filiere.label) & Q(anuniv=lan))
    aniveau=get_object_or_404(Niveau,Q(code=niveau.code) & Q(filiere=anfil))
    
    context={}
    try:
        etudiant=get_object_or_404(Etudiant,Q(etudiantid=etudiantid))
        resetud=Resultat.objects.filter(etudiant=etudiant)
        context['nompren']=etudiant.nompren
        if resetud.count()==0:
            context['statut']=6
            context['nban']=1
        else:
            try:
                res=get_object_or_404(Resultat,Q(etudiant=etudiant) & Q(maxan=lan) & Q(niveau=aniveau))
                context['statut']=res.statut.id
                if res.statut.id==3:
                    context['erreur']=False
                    context['nban']=res.nban+1
                if res.statut.id==4:
                    context['erreur']=True
        
            except:
                maxniv=Resultat.objects.filter(Q(etudiant=etudiant) & Q(maxan=lan)).aggregate(max=Max('niveau'))
                niveau=Niveau.objects.get(nivid=maxniv['max'])
                res=Resultat.objects.get(Q(etudiant=etudiant) & Q(maxan=lan) & Q(niveau=niveau))
                if res.statut.id<3:
                    context['statut']=6
                    context['nban']=1
                else:
                    context['statut']=res.statut.id
                    context['nban']=res.nban
                if res.statut.id==4:
                    context['erreur']=True
                elif res.statut.id<3:
                    context['erreur']=False 

    except:
        context['erreur']=True
        return JsonResponse(context)
    print(context)
    return JsonResponse(context)

def get_compos_ses1(compid):
    compos=Composition.objects.get(compid=compid.compid)
    examen=compos.examen
    cm=Compotype.objects.get(id=1)
    compos1=get_object_or_404(Composition,Q(examen__session=1) & Q(ecue=compos.ecue) & Q(examen__anuniv=compos.examen.anuniv) & Q(comptype=cm) & Q(examen__niveau=compos.examen.niveau))
    return compos1

def get_deja_valide(compo):
    dejaca=Moyenne_ue_cm.objects.filter(Q(moyenne__gte=10) & Q(examen=compo.examen)).values('etudiant')
    return dejaca




def get_random_list(compid):
    n=anotmp.objects.all()
    if n:
        n.delete()
    compos=Composition.objects.get(compid=compid.compid)
    examen=compos.examen
    effectif=compos.effectif
    data=range(compos.fano,compos.lano)
    dn=random.sample(range(compos.fano, compos.lano+1), compos.effectif)
    print(dn)
    j=0
    anuniv=compos.examen.niveau.filiere.anuniv
    admis=Resultat_info.objects.get(id=1)
    compense=Resultat_info.objects.get(id=1)
    session=compos.examen.session
    dejaadmis=Notes_Ue.objects.filter((Q(resultat=admis)|Q(resultat=compense)) & Q(examen__ue__code=compos.examen.ue.code) & Q(examen__niveau__code=compos.examen.niveau.code)).values('etudiant')
   
    if session==1:
        et=Inscription.objects.filter(Q(niveau=compos.examen.niveau) & Q(anuniv=compos.examen.niveau.filiere.anuniv)).exclude(etudiant__in=dejaadmis).values('etudiant').distinct('etudiant')

    if session==2:
        cm=Compotype.objects.get(id=1)
        compos1=get_compos_ses1(compid)
        dejaca=get_deja_valide(compos1)
        et=Inscription.objects.filter(Q(niveau=compos.examen.niveau) & Q(anuniv=compos.examen.niveau.filiere.anuniv)).exclude(etudiant__in=dejaadmis).values('etudiant').distinct('etudiant')
        et=et.exclude(etudiant__in=dejaca)
        print(et)
        
       

    for d in dn:
        etid=et[j]
        etudiant=Etudiant.objects.get(etudiantid=etid['etudiant'])
        a=anotmp.objects.create(ano=d,etudiant=etudiant,rang=j)
        a.save()
        j=j+1

    at=anotmp.objects.all()
    ano=Anonymat.objects.filter(composition=compos).count()

    if ano==0:
        for a in at:
            print(a.etudiant)
            a=Anonymat.objects.create(ano=a.ano, etudiant=a.etudiant, composition=compos,anuniv=anuniv)
            a.save()
        


def printAnoIdent(request,compid):
    compos=Composition.objects.get(compid=compid)
    anos=Anonymat.objects.filter(Q(composition=compos) & Q(etudiant__isnull=False)).order_by('ano')
    buffer = io.BytesIO()
    niveau=compos.ecue.ue.niveau
    response = HttpResponse(content_type = 'application/pdf')
    response['Content-Disposition'] = 'inline; filename = "'+niveau.code+compos.ecue.ue.code+compos.ecue.code+'.pdf"'
    doc = SimpleDocTemplate(buffer,   pagesizes = A4,topMargin=1, bottomMargin=1,)
    story = []
    data=[]
    style=[]
    style=[]
    style.append(('GRID',  (0,  0),  (-1,  -1),  0.5,  colors.black))
    style.append(('FONTSIZE',   (0,   0),   (-1,   -1),   7))
    style.append(('VALIGN',   (0,   0),   (-1,   -1),   'MIDDLE')) 
    rowstart=0
    rowend=0
    j=0
    splab = ParagraphStyle('parrafos',   
              alignment = TA_LEFT,  
              fontSize = 8,  
              fontName = "Times-Roman")
    splab2 = ParagraphStyle('parrafos',   
              alignment = TA_CENTER,  
              fontSize = 12,  
              fontName = "Times-Roman")
    header = Paragraph("<b>Listing des anonymats</b>",   splab2)
    story.append(header)
    nivstr = Paragraph("<b>"+niveau.labels+"</b>",   splab2)
    story.append(nivstr)
    uestr = Paragraph("<b>"+compos.ecue.ue.labels+"</b>",   splab2)
    story.append(uestr)
    ecuestr = Paragraph("<b>"+compos.ecue.labels+"</b>",   splab2)
    story.append(ecuestr)
    ecuecode = Paragraph("<b>"+compos.ecue.code+"</b>",   splab2)
    story.append(ecuecode)

    for a in anos:
        line=[]
        line.append(a.etudiant.nce)
        line.append(Paragraph(a.etudiant.nompren,splab))
        line.append(str(a.ano))
        data.append(line)

        j=j+1
    t = Table(data,   colWidths = [5*cm,  9*cm,   3*cm], rowHeights=0.6*cm)
    t.setStyle(TableStyle(style))
    
    story.append(t)
    doc.build(story)
        
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def export_inscr_excel(request,niveauid):
    response = HttpResponse(content_type='text/csv')
    niveau=Niveau.objects.get(nivid=niveauid)
    filename="Liste_inscrit_"+niveau.code+".csv"
    response['Content-Disposition'] = 'attachment; filename="'+filename+'"'
    writer=csv.writer(response, delimiter=';')
    writer.writerow(["Num","NCE","NOM","PRENOMS","Date de naissance","Lieu de naissance"])
    etlist=Inscription.objects.filter(niveau=niveau).order_by('etudiant__nompren')
    j=1
    for et in etlist:
        writer.writerow([j,et.etudiant.nce,et.etudiant.nom,et.etudiant.prenoms,et.etudiant.ddnais,et.etudiant.lnais])
        j=j+1
    return response

import xlsxwriter
import zipfile
import shutil
def export_anonymat(request,niveauid):
    niveau=Niveau.objects.get(nivid=niveauid)
    examen=Examen.objects.filter(niveau=niveau)
    code=niveau.code
    session=0
    message=" Les fichiers des anonymats suivant de "+niveau.code+":\n"
    to_list=['danhofr@gmail.com','setiho@hotmail.com','eloik@yahoo.fr','ahuerod.inf@univ-na.ci ']
    n=0
    for e in examen:
        path="/home/ufr-sn/Documents/anonymat/fichiers/"+code+"/session"+str(e.session)+"/"+e.ue.code
        session=e.session
        try:
            os.makedirs(path)
        except OSError:
            print(path)
        compos=Composition.objects.filter(Q(examen=e) & Q(ano=True) & Q(exporter=False))
       
        for c in compos:
            filename=path+"/"+c.ecue.code+".xlsx"
            print(filename)
            message=message+"\t -"+c.comptype.labels+" de " +c.ecue.code+"("+c.ecue.ue.code+")\n"
            workbook = xlsxwriter.Workbook(filename)
            worksheet = workbook.add_worksheet(c.ecue.code)
            ano=Anonymat.objects.filter(composition=c).values_list('ano').order_by('ano')
            row=0
            col=0
            worksheet.write(row, col,"Anonymat")
            col=1
            worksheet.write(row, col,"Notes")
            col=1
            row=1
            for a in ano:
                col=0
                worksheet.write(row, col,a[0])
                col=1
                worksheet.write(row, col,0)
                row+=1
                
            workbook.close()
            c.exporter=True
            c.save()
        n+=1
    path="/home/ufr-sn/Documents/anonymat/fichiers/"+code+"/session"+str(e.session)
    output=path+"/"+code+str(session)
    shutil.make_archive(output, 'zip', path)
    emailrep=niveau.responsable
    message=message+" sont disponibles.\n"
    message=message+"Ce message est généré automatiquement par le système"
    sujet="Fichiers des anonymats"
    if emailrep==None:
        pass
    else:
        to_list.append(emailrep)
        
    email=EmailMessage(sujet,
        message,
        to=to_list
    )
    email.attach_file(output+".zip")
    if n>0:
        email.send()
    return HttpResponseRedirect(reverse('examlist',args=(niveauid,session)))



        
def check_action(request):
    id=request.GET.get("dataid")
    res_id=request.GET.get("resid")
    note=Notes_Ue.objects.get(id=id)
    new_res=Resultat_info.objects.get(id=res_id)
    reponse='OK'
    
    if res_id==1 and note.moyenne>10:
        reponse='ATTENTION'
    if res_id==4:
        r= get_object_or_404(Resultat_bigcat, Q(etudiant=note.etudiant) & Q(niveau=note.examen.niveau) & Q(semestre=note.examen.ue.semestre))
    context={}
    context['response']=minano
    return JsonResponse(context)


def export_historic(request):
    response = HttpResponse(content_type='text/csv')
    histo=Notes_Ue.objects.all()
    filename="historique.csv"
    response['Content-Disposition'] = 'attachment; filename="'+filename+'"'
    writer=csv.writer(response, delimiter=';')
    writer.writerow(["ORDRE","NCE","NOM","PRENOMS","DATE DE NAISSANCE","LIEU DE NAISSANCE","NIVEAU","UE","MOYENNE","RESULTAT"])
    j=1
    total=histo.count()
    for h in histo:
        writer.writerow([j,h.etudiant.nce,h.etudiant.nom,h.etudiant.prenoms,h.etudiant.ddnais,h.etudiant.lnais,h.examen.niveau.code,h.examen.ue.code,h.moyenne,h.resultat.labels])
        j=j+1
        total=total-1
        
    return response

def openform_scolarite(request,niveauid):
    niveau=Niveau.objects.get(nivid=niveauid)
    anuniv=niveau.filiere.anuniv
    context={
        'niveau':niveau.nivid,
        'anuniv':anuniv,
    }
    
    return render(request,'notes3/inscription_scolarite.html',context)
    

def import_fichier_scolarite(request,niveauid):
    niveau=Niveau.objects.get(nivid=niveauid)
    if 'GET'==request.method:
        pass
    else:
        excel_file=request.FILES["excel_file"]
        data=get_data(excel_file)
        prefix=niveau.code
        sheet=data[prefix]
        anuniv=niveau.filiere.anuniv
        for row in sheet:
                if len(row)==0:
                            break
                if len(row[0].strip())<12:
                    pass
                else:
                    if len(row[0].strip())==12:
                        print(row[0])
                        etid=int(row[0][-8:].strip())
                        nom=row[1]
                        prenoms=row[2]
                        ddnais=row[3]
                        lnais=row[4]
                        if row[5]=='F':
                            sexe=Sexe.objects.get(id=2)
                        if row[5]=='M':
                            sexe=Sexe.objects.get(id=1)
                      
                        maj=True
                        nompren=nom+' '+prenoms
                         
                        obj,created=Etudiant.objects.update_or_create(
                                    etudiantid=etid,
                                    defaults={'nom':nom,'prenoms':prenoms,'ddnais':ddnais,'lnais':lnais,'sexe':sexe,'maj':maj,'curau':True}
                                 )
                        etudiant=Etudiant.objects.get(etudiantid=etid)
                        s=get_nivstat(etid,niveau.filiere.anuniv.auid,niveau.nivid)
                        statut=Statut_info.objects.get(id=s['statid'])
                        nban=s['nban']
                        niveau=niveau
                        anuniv=niveau.filiere.anuniv
                        obj,created=Inscription.objects.update_or_create(
                                niveau=niveau,
                                anuniv=anuniv,
                                etudiant=etudiant,
                                defaults={'inscrit':True,'cfc':etudiant.cfc,'nban':nban,'statut':statut}
                        )
    
    return HttpResponseRedirect(reverse('linscrire',args=(niveauid,)))



def openform_cfc(request,niveauid):
    niveau=Niveau.objects.get(nivid=niveauid)
    anuniv=niveau.filiere.anuniv
    context={
        'niveau':niveau.nivid,
        'anuniv':anuniv,
    }
    
    return render(request,'notes3/inscription_cfc.html',context)

def import_cfc(request,niveauid):
    niveau=Niveau.objects.get(nivid=niveauid)
    if 'GET'==request.method:
        pass
    else:
        excel_file=request.FILES["excel_file"]
        data=get_data(excel_file)
        prefix=niveau.code
        sheet=data[prefix]
        anuniv=niveau.filiere.anuniv
        for row in sheet:
                if len(row)==0:
                            break
                if len(row[0].strip())<12:
                    pass
                else:
                    if len(row[0].strip())==12:
                        etid=int(row[0][-8:].strip())
                        try:

                            etudiant=Etudiant.objects.get(etudiantid=etid)
                            etudiant.cfc=True
                            s=get_nivstat(etid,niveau.filiere.anuniv.auid,niveau.nivid)
                            if s['statid']==4:
                                statut=Statut_info.objects.get(id=8)
                            nban=s['nban']+1
                            niveau=niveau
                            anuniv=niveau.filiere.anuniv
                            obj,created=Inscription.objects.update_or_create(
                                niveau=niveau,
                                anuniv=anuniv,
                                etudiant=etudiant,
                                defaults={'inscrit':True,'cfc':etudiant.cfc,'nban':nban,'statut':statut}
                            )
                        except:
                            pass
    
    return HttpResponseRedirect(reverse('linscrire',args=(niveauid,)))




class incription_update(UpdateView):
    model=Inscription
    slug_field='id'
    fields=['inscrit','cfc']
    template_name_suffix='_update_form'
  
    def get_success_url(self):
        niveauid=self.object.niveau.nivid
        return reverse('linscrire',args=(int(niveauid),))
        


class Inscription_create2(CreateView):
    model=Inscription
    form_class=iForms2
    template_name="notes3/inscriptions_etudiant.html"

    def get_context_data(self, **kwargs):
        context=super(Inscription_create2,self).get_context_data(**kwargs)
        auid=self.kwargs['auid']
        context['curau']=auid
        return context


    def get_initial(self):
        initial=super(Inscription_create2, self).get_initial()
        initial=initial.copy()
        initial['anuniv']=self.kwargs['auid']
        initial['etudiant']=self.kwargs['etudiantid']
        etudiantid=self.kwargs['etudiantid']
        etudiant=Etudiant.objects.get(etudiantid=etudiantid)
        print(etudiant.epss)
        if etudiant.epss==True:
            initial['nban']=2
            initial['statut']=3
        else:
            initial['nban']=1
            initial['statut']=6
        return initial
    def get_success_url(self, **kwargs):
        etudiantid=self.object.etudiant.etudiantid
        return reverse_lazy('resultats', args=(etudiantid,))


def list_ajourne_ecue(examid):
    
    ajourne=Resultat_info.objects.get(id=3)
    examen=get_object_or_404(Examen,Q(id=examid))
    if examen.session==2:
        examses1=get_object_or_404(Examen,Q(ue=examen.ue) & Q(session=1))
        etudajour=Notes_Ue.objects.filter(Q(examen=examses1) & Q(resultat=ajourne)).values_list('etudiant')
        compos=Moyenne_ecue_cm.objects.filter(Q(examen=examses1) & Q(etudiant__in=etudajour)).distinct('composition')
        
    else:
        etudajour=Notes_Ue.objects.filter(Q(examen=examen) & Q(resultat=ajourne)).values_list('etudiant')
        compos=Moyenne_ecue_cm.objects.filter(Q(examen=examen) & Q(etudiant__in=etudajour)).distinct('composition')
        
    for c in compos:
        etud=Moyenne_ecue_cm.objects.filter(Q(etudiant__in=etudajour) & Q(moyenne__lt=10) & Q(composition=c.composition))



def set_student_salle(examenid):
    examen=get_object_or_404(Examen,Q(id=examenid))
    dejaadmis=Notes_Ue.objects.filter(Q(resultat__id__lt=3) & Q(examen__ue__code=examen.ue.code) & Q(examen__niveau__code=examen.niveau.code)).values('etudiant')
    etud=Inscription.objects.filter(Q(niveau=examen.niveau) & Q(anuniv=examen.anuniv)).exclude(etudiant__in=dejaadmis)
    nb=etud.count()
    dn=random.sample(range(1, nb+1),nb)
    j=0
    dis=Dispaching.objects.filter(examen=examen)
    if dis:
        dis.delete()
    for et in etud:
        d=Dispaching.objects.create(etudiant=et.etudiant,rang=dn[j],examen=examen)
        j=j+1
        d.save()

def salle_list_dispaching(request,examid):
    context={}
    context['examid']=examid
    salle=Salle.objects.all().order_by('nom')
    context['salles']=salle

    return render(request,'notes3/dispaching.html',context)

        
def dispaching(request,examid,salleid):
    salle=get_object_or_404(Salle,Q(id=salleid))
    dejad=Dispaching.objects.filter(salle__isnull=True).count()
    nombre=salle.place
    print(dejad)

    if dejad==0:
        set_student_salle(examid)
        Dispaching.objects.filter(rang__lte=nombre).update(salle=salle)
    else:
        print('test')
        maxrng=Dispaching.objects.filter(salle__isnull=False).aggregate(maxrang=Max('rang'))
        mrg=maxrng['maxrang']
        print(mrg)
        minr=mrg
        mxrg=minr+nombre
        print(minr,mxrg)
        Dispaching.objects.filter(Q(rang__gt=minr) & Q(rang__lte=mxrg)).update(salle=salle)
    salle.dispach=True
    return HttpResponseRedirect(reverse('sallex',args=(examid,)))

def export_dispatching(request,examid):
    response = HttpResponse(content_type='text/csv')
    examen=get_object_or_404(Examen,Q(id=examid))
    salle_list=Dispaching.objects.filter(examen=examen).distinct('salle')
    print(salle_list)
    for salle in salle_list:
        dispach=Dispaching.objects.filter(salle=salle.salle).values_list('etudiant')
        filename='/home/ufr-sn/Documents/Dispaching_'+salle.salle.nom+'_'+examen.niveau.code+examen.ue.code+str(examen.session)+".csv"
        f=open(filename,'w')
        writer=csv.writer(f, delimiter=';')
        writer.writerow([salle.salle.nom])
        writer.writerow(["ORDRE","NCE","NOM","PRENOMS","DATE DE NAISSANCE","LIEU DE NAISSANCE"])
        etlist=Etudiant.objects.filter(etudiantid__in=dispach).order_by('nom','prenoms')
        j=1
        
        for et in etlist:
            writer.writerow([j,et.nce,et.nom,et.prenoms,et.ddnais,et.lnais])
            j=j+1
        f.close()

    return HttpResponse('Fichier imprimé')

def check_session_1(request):
    examid=request.GET.get("examenid")
    ecueid=request.GET.get("ecueid")
    ecue=UeInfo.objects.get(uei=ecueid)
    examen=Examen.objects.get(id=examid)
    examen1=get_object_or_404(Examen,Q(session=1) & Q(ue__code=examen.ue.code) & Q(anuniv=examen.anuniv) & Q(niveau=examen.niveau))
    ncomp=Composition.objects.filter(Q(examen=examen1) & Q(ecue=ecue)).count()
    context={}
    context['ncomp']=ncomp
    return JsonResponse(context)

