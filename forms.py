"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from notes3.models import Examen, AnUniv, Ue, UeInfo, UeCat, Sexe, Composition, Inscription, Notes_Ue, tmpnote,Anonymat, Etudiant, Notes_ecue, Niveau, Salle, Enseignant, Heures,Statut_info
import datetime

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))
class examform(forms.ModelForm):
    anuniv=forms.IntegerField()
    niveau=forms.IntegerField()
    examdate=forms.DateField(initial=datetime.date.today)
    class Meta:
        model=Examen
        fields=['id','anuniv','niveau','session','ue','examdate','ecue_ignored','afficher']
    def clean_anuniv(self):
        au=self.cleaned_data['anuniv']
        anuniv=AnUniv.objects.get(auid=au)
        return anuniv
    def clean_niveau(self):
        niv=self.cleaned_data['niveau']
        niveau=Niveau.objects.get(nivid=niv)
        return niveau
    
class rexamform(forms.ModelForm):
    class Meta:
        model=Examen
        fields=['id','anuniv','niveau','session','ue','examdate','ecue_ignored','afficher','calcmode']
   
    
class AnUnivform(forms.ModelForm):
    class Meta:
        model=AnUniv
        fields=['auid','labels','curau','lauid']
   
   
        labels = {
            "auid": _("Identifiant"),
            "labels": _("Labels"),
            "curau": _("Années courante"),
            "lauid": _("Années précédente"),    
        }
   
            
class compoform(forms.ModelForm):
    compostdate=forms.DateField(initial=datetime.date.today)
    examen=forms.IntegerField()
    class Meta:
        model=Composition
        fields=['compid','examen','effectif','genano','comptype','ecue','fano','lano','ano','compostdate','ecue_ignored','coefficient','session','version']
    def clean_examen(self):
        examid=self.cleaned_data['examen']
        examen=Examen.objects.get(id=examid)
        return examen
    
   
class anoform(forms.ModelForm):
    etudiant=forms.IntegerField()

    class Meta:
        model=Anonymat
        fields=['etudiant','ano','error']
    def clean_etudiant(self):
        etid=self.cleaned_data['etudiant']
        etudiant=Etudiant.objects.get(etudiantid=etid)
        return etudiant

   
class tnoteform(forms.ModelForm):
    etudiant=forms.IntegerField()
    composition=forms.IntegerField()
    class Meta:
        model=tmpnote
        fields=['etudiant','idtmp','nompren','composition']
    def clean_etudiant(self):
        etid=self.cleaned_data['etudiant']
        etudiant=Etudiant.objects.get(etudiantid=etid)
        return etudiant
    def clean_composition(self):
        compid=self.cleaned_data['composition']
        composition=Composition.objects.get(compid=compid)
        return composition

class notesform(forms.ModelForm):
    etudiant=forms.IntegerField()
    composition=forms.IntegerField()
    anonymat=forms.IntegerField()
    class Meta:
        model=Notes_ecue
        fields=['etudiant','note','composition','anonymat']
    def clean_composition(self):
        cid=self.cleaned_data['composition']
        composition=Composition.objects.get(compid=cid)
        return composition
    def clean_etudiant(self):
        etid=self.cleaned_data['etudiant']
        etudiant=Etudiant.objects.get(etudiantid=etid)
        return etudiant
    def clean_anonymat(self):
        ano=self.cleaned_data['anonymat']
        anonymat=Anonymat.objects.get(ano=ano)
        return anonymat

class tdtp_notesform(forms.ModelForm):
    etudiant=forms.IntegerField()
    composition=forms.IntegerField()
    class Meta:
        model=Notes_ecue
        fields=['etudiant','note','composition']
    def clean_composition(self):
        cid=self.cleaned_data['composition']
        composition=Composition.objects.get(compid=cid)
        return composition
    def clean_etudiant(self):
        etid=self.cleaned_data['etudiant']
        etudiant=Etudiant.objects.get(etudiantid=etid)
        return etudiant


class oneanoform(forms.ModelForm):
    ano=forms.IntegerField()
    etudiant=forms.IntegerField()
    class Meta:
        model=Anonymat
        fields=['ano','etudiant','composition']
    def clean_etudiant(self):
        etid=self.cleaned_data['etudiant']
        etudiant=Etudiant.objects.get(etudiantid=etid)
        return etudiant
class salleform(forms.ModelForm):
    class Meta:
        model=Salle
        fields=['nom','place','utiliser']

class enseigform(forms.ModelForm):
    class Meta:
        model=Enseignant
        fields=['emploi','nompren','email','contact']

class horaireform(forms.ModelForm):
    class Meta:
        model=Heures
        fields=['enseignant','cdate','niveau','ue','ecues','debut','fin']

class etudiantForm(forms.Form):
    etudiantid=forms.IntegerField(label='Identifiant')

class CetudiantForm(forms.ModelForm):
    class Meta:
        model=Etudiant
        fields=['etudiantid','nom','prenoms','ddnais','lnais','sexe', 'curau','epss','cfc','dut']
  
            
class delibform(forms.Form):
    delib=forms.IntegerField()

class ecueform(forms.ModelForm):

    class Meta:
        model=UeInfo
        fields=['code','labels','ue','inuse','niveau','ecue_ignored']
        widgets = { 'labels': forms.TextInput(attrs={'size': 300})}
   
class addecueform(forms.ModelForm):

    class Meta:
        model=UeInfo
        fields=['code','labels','ue','inuse','uei','credits','ecue_ignored','niveau']
        widgets = { 'labels': forms.TextInput(attrs={'size': 300})}


class etform(forms.Form):
    class Meta:
        fields=['nom','prenoms','ddnais','lnais']

class delibform(forms.Form):
    class Meta:
        model=Examen
        fields=['delibdate','delib']
class formprint(forms.Form):
    prt_opt=forms.ChoiceField(widget=forms.RadioSelect(), choices=[(1, 'Portrait'), (2, 'Paysage')])
class ueform(forms.ModelForm):
    class Meta:
        model=Ue
        fields=['code','labels','inuse','semestre','uecat','credits','biguecat']

class ueAddform(forms.ModelForm):
    class Meta:
        model=Ue
        fields=['ueid','code','labels','inuse','niveau','uecat','semestre','credits','biguecat','lastan']
    


class formReclamation(forms.Form):
    etudiantid=forms.IntegerField(label='Identifiant')


class formlisting(forms.Form):
    first=forms.IntegerField(label="Premier anonymat")



class addnote(forms.ModelForm):
    examen=forms.IntegerField(label='Choisir un examen')
    etudiant=forms.IntegerField(label='Etudiant')
    class Meta:
        model=Notes_Ue
        fields=['examen','moyenne','resultat','etudiant']
    def clean_examen(self):
        exid=self.cleaned_data['examen']
        examen=Examen.objects.get(id=exid)
        return examen
    def clean_etudiant(self):
        etid=self.cleaned_data['etudiant']
        etudiant=Etudiant.objects.get(etudiantid=etid)
        return etudiant
class upnote(forms.ModelForm):
    examen=forms.IntegerField(label='Choisir un examen')
    class Meta:
        model=Notes_Ue
        fields=['examen','moyenne','resultat','id']
    def clean_examen(self):
        exid=self.cleaned_data['examen']
        examen=Examen.objects.get(id=exid)
        return examen
Examen
class InscrForm(forms.ModelForm):
    class Meta:
        model=Inscription
        fields=['etudiant','niveau','anuniv','statut','nban']



class iForms(forms.ModelForm):
    etudiant=forms.IntegerField()
    anuniv=forms.IntegerField()
    niveau=forms.IntegerField()
    statut=forms.IntegerField()

    class Meta:
        model=Inscription
        fields=['etudiant','niveau','anuniv','statut','nban']
    def clean_statut(self):
        id=self.cleaned_data['statut']
        print(id)
        statut=Statut_info.objects.get(id=id)
        return statut
    def clean_anuniv(self):
        aid=self.cleaned_data['anuniv']
        anuniv=AnUniv.objects.get(auid=aid)
        return anuniv
    def clean_etudiant(self):
        etid=self.cleaned_data['etudiant']
        etudiant=Etudiant.objects.get(etudiantid=etid)
        return etudiant
    def clean_niveau(self):
        nivid=self.cleaned_data['niveau']
        niveau=Niveau.objects.get(nivid=nivid)
        return niveau

class iForms(forms.ModelForm):
    etudiant=forms.IntegerField()
    anuniv=forms.IntegerField()
    niveau=forms.IntegerField()
    statut=forms.IntegerField()

    class Meta:
        model=Inscription
        fields=['etudiant','niveau','anuniv','statut','nban']


class iupForms(forms.ModelForm):

    class Meta:
        model=Inscription
        fields=['inscrit','cfc']


class iForms(forms.ModelForm):
    etudiant=forms.IntegerField()
    anuniv=forms.IntegerField()
    niveau=forms.IntegerField()
    statut=forms.IntegerField()

    class Meta:
        model=Inscription
        fields=['etudiant','niveau','anuniv','statut','nban']
    def clean_statut(self):
        id=self.cleaned_data['statut']
        print(id)
        statut=Statut_info.objects.get(id=id)
        return statut
    def clean_anuniv(self):
        aid=self.cleaned_data['anuniv']
        anuniv=AnUniv.objects.get(auid=aid)
        return anuniv
    def clean_etudiant(self):
        etid=self.cleaned_data['etudiant']
        etudiant=Etudiant.objects.get(etudiantid=etid)
        return etudiant
    def clean_niveau(self):
        nivid=self.cleaned_data['niveau']
        niveau=Niveau.objects.get(nivid=nivid)
        return niveau

class iForms2(forms.ModelForm):
    etudiant=forms.IntegerField()
    anuniv=forms.IntegerField()
    niveau=forms.IntegerField()
    statut=forms.IntegerField()

    class Meta:
        model=Inscription
        fields=['etudiant','niveau','anuniv','statut','nban','cfc']

    def clean_statut(self):
        id=self.cleaned_data['statut']
        print(id)
        statut=Statut_info.objects.get(id=id)
        return statut
    def clean_anuniv(self):
        aid=self.cleaned_data['anuniv']
        anuniv=AnUniv.objects.get(auid=aid)
        return anuniv
    def clean_etudiant(self):
        etid=self.cleaned_data['etudiant']
        etudiant=Etudiant.objects.get(etudiantid=etid)
        return etudiant
    def clean_niveau(self):
        nivid=self.cleaned_data['niveau']
        niveau=Niveau.objects.get(nivid=nivid)
        return niveau
