# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.db.models import Q, Count, Sum, Max, Min, F,Subquery, OuterRef
from django.utils import timezone
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime
from django.db.models.signals import post_init
from django_currentuser.middleware import (
    get_current_user, get_current_authenticated_user)
from django_currentuser.db.models import CurrentUserField

class Statut_info(models.Model):
    labels = models.CharField(max_length=25)
    class Meta:
        db_table = 'statut_infos'
    def __str__(self):
        return self.labels


class AnUniv(models.Model):
    auid = models.IntegerField(primary_key=True)
    labels = models.CharField(max_length=9)
    curau = models.BooleanField()
    precau = models.BooleanField(null=True)
    lauid = models.IntegerField()
    finish=models.BooleanField(default=False)
    inscrit=models.BooleanField(default=False,null=True)

    class Meta:
        db_table = 'anuniv'
    def __str__(self):
        return self.labels
    def save(self, *args, **kwargs):
        if self.finish==True:
            self.curau=False
        if self.curau==True:
            self.finish=False
        super(AnUniv, self).save(*args, **kwargs)

class Filiere(models.Model):
    filid = models.IntegerField(primary_key=True)
    label = models.CharField(max_length=254)
    domaine = models.CharField(max_length=65)
    mention = models.CharField(max_length=65)
    specialite = models.CharField(max_length=65)
    debut = models.IntegerField(null=True)
    fin = models.IntegerField(null=True)
    responsable=models.EmailField(null=True)
    anuniv=models.ForeignKey(AnUniv,on_delete=models.DO_NOTHING,null=True)
    
    class Meta:
        db_table = 'filieres'

class Sexe(models.Model):
    label=models.CharField(max_length=12)
    code=models.CharField(max_length=1,null=True)
    class Meta:
        db_table = 'sexes'
    def __str__(self):
        return self.code

class Etudiant(models.Model):
    etudiantid = models.IntegerField(primary_key=True)
    nce = models.CharField(max_length=12, blank=True, null=True)
    nom = models.CharField(max_length=65, blank=True, null=True)
    prenoms = models.CharField(max_length=254, blank=True, null=True)
    ddnais = models.DateField(blank=True, null=True)
    lnais = models.CharField(max_length=125, blank=True, null=True)
    sexeid = models.IntegerField(blank=True, null=True)
    curau = models.BooleanField()
    nompren = models.CharField(max_length=254, blank=True, null=True)
    epss=models.BooleanField(default=False,null=True)
    cfc=models.BooleanField(default=False)
    sexe=models.ForeignKey(Sexe,on_delete=models.DO_NOTHING,null=True)
    maj=models.BooleanField(default=True,null=True)
    dut=models.BooleanField(default=False,null=True)
    class Meta:

        db_table = 'etudiants'
    def __str__(self):
        return self.nce 
    def save(self, *args, **kwargs):
        self.nce="CI02"+str(self.etudiantid)
        self.nompren=self.nom+" "+self.prenoms
        super(Etudiant, self).save(*args, **kwargs)


class Niveau(models.Model):
    nivid = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=8)
    labels = models.CharField(max_length=125)
    option = models.CharField(max_length=125, blank=True, null=True)
    grade = models.CharField(max_length=1)
    nivgrade = models.IntegerField()
    passto = models.IntegerField(blank=True, null=True)
    nbres = models.IntegerField()
    filiere = models.ForeignKey(Filiere, models.DO_NOTHING)
    responsable=models.EmailField(null=True)
    coeftp=models.IntegerField(null=True)
    coefcm=models.IntegerField(null=True)
    coeftd=models.IntegerField(null=True)
    conseiller=models.EmailField(null=True)
    nivto=models.CharField(null=True,max_length=25)
    minano=models.IntegerField(null=True)
    maxano=models.IntegerField(null=True)
    effectif=models.IntegerField(null=True,default=1)
    nbrecopy=models.BigIntegerField(null=True)
    tp=models.BooleanField(default=True,null=True)
    cycle=models.IntegerField(default=1,null=True)
    
    

    class Meta:
        db_table = 'niveaux'
    def __str__(self):
        return self.code
class Niveau_from_to(models.Model):
    nifid = models.AutoField(primary_key=True)
    niveaufrom = models.ForeignKey(Niveau, models.DO_NOTHING,null=True,related_name='niveaufrom')
    niveauto=models.ForeignKey(Niveau, models.DO_NOTHING,null=True,related_name='niveauto')
    niveau=models.ForeignKey(Niveau, models.DO_NOTHING,null=True,related_name='niveau')
    grade=models.IntegerField(null=True)
    
    class Meta:
        db_table = 'niveaux_from_to'
class BigUeCat(models.Model):
    bcid = models.IntegerField(primary_key=True)
    categorie = models.CharField(max_length=25)
   
    class Meta:
        db_table = 'big_categories'
    def __str__(self):
        return self.categorie
class UeCat(models.Model):
    uecid = models.IntegerField(primary_key=True)
    categorie = models.CharField(max_length=25)
    bicategorie=models.CharField(max_length=25,null=True)

    class Meta:
        db_table = 'categories'
    def __str__(self):
        return self.categorie
class Ue(models.Model):
    sess = (
    (1, 'Première'),
    (2, 'Seconde'),
    (3, 'Troisième'),
    (4, 'Quatrième'),
    (5, 'Cinquième'),
    (6, 'Sixième'),
    )
    ueid = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=6)
    labels = models.CharField(max_length=254)
    semestre = models.IntegerField(choices=sess)
    hcm = models.IntegerField(blank=True, null=True)
    htp = models.IntegerField(blank=True, null=True)
    htd = models.IntegerField(blank=True, null=True)
    tpe = models.IntegerField(blank=True, null=True)
    credits = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    niveau = models.ForeignKey(Niveau, models.DO_NOTHING)
    uecat = models.ForeignKey(UeCat, models.DO_NOTHING)
    inuse=models.BooleanField(null=True)
    coefcm=models.IntegerField(null=True)
    coeftp=models.IntegerField(null=True)
    coeftd=models.IntegerField(null=True)
    biguecat=models.ForeignKey(BigUeCat,null=True,on_delete=models.DO_NOTHING)
    uelibre=models.BooleanField(default=False,null=True)
    lastan=models.IntegerField(null=True)
    class Meta:
        db_table = 'ues'
    def __str__(self):
        return self.labels
    def get_absolute_url(self):
        return reverse('listue',args=[self.niveau.nivid])
    def save(self, *args, **kwargs):
        if self.credits<=3:
            self.biguecat.bcid=1
        elif self.credits>3:
            self.biguecat.bcid=2
        super(Ue, self).save(*args, **kwargs)

class UeInfo(models.Model):
    uei = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=6)
    labels = models.CharField(max_length=254)
    credits = models.DecimalField(max_digits=3, decimal_places=1)
    debut = models.IntegerField(blank=True, null=True)
    fin = models.IntegerField(blank=True, null=True)
    ecue_ignored = models.BooleanField()
    niveau = models.ForeignKey(Niveau, models.DO_NOTHING, blank=True, null=True)
    ue = models.ForeignKey(Ue, models.DO_NOTHING)
    inuse=models.BooleanField(null=True)
    coefcm=models.IntegerField(null=True)
    coeftp=models.IntegerField(null=True)
    coeftd=models.IntegerField(null=True)
    class Meta:
        db_table = 'ueinfos'

    def __str__(self):
        return self.labels+' ('+self.code+')'
    def get_absolute_url(self):
        return reverse('listecue', args=[self.ue.ueid])
    def save(self, *args, **kwargs):
        if self.niveau.nivid<=12:
            self.coefcm=2
            self.coeftd=1
            self.coeftp=1
        else:
            self.coefcm=2
            self.coeftd=1
            self.coeftp=2
        super(UeInfo, self).save(*args, **kwargs)


class Resultat_grade(models.Model):
    grade = models.CharField(max_length=1)
    credit = models.DecimalField(max_digits=6, decimal_places=2)
    nban = models.IntegerField()
    statut = models.IntegerField(blank=True, null=True)
    etudiant = models.ForeignKey(Etudiant, models.DO_NOTHING)
    maxan = models.ForeignKey(AnUniv, models.DO_NOTHING)
    niveau = models.ForeignKey(Niveau, models.DO_NOTHING, blank=True, null=True)
    

    class Meta:
        
        db_table = 'Resultat_grade'
        unique_together = (('etudiant', 'grade'),)

class Compotype(models.Model):
    code = models.CharField(max_length=2)
    labels = models.CharField(max_length=25)
    coef = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'compotype'
    def __str__(self):
        return self.code

class Examen(models.Model):
    sess = (
    (1, 'Première'),
    (2, 'Seconde'),
    )

    calculs = (
        (1, 'La moyenne pondérée des composition'),
        (2, 'Moyenne des ECUE'),
        (3, 'Moyenne des CM et TP'),
    )
    id=models.IntegerField(default=0, primary_key=True)
    session = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(2)] ,choices=sess)
    examdate = models.DateField()
    delibdate = models.DateField(blank=True, null=True)
    delib_cm = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True,verbose_name="Barre de délibération")
    nbadmis = models.IntegerField(blank=True, null=True)
    coefficient = models.IntegerField(blank=True, null=True)
    calcul = models.BooleanField(default=False)
    finish = models.BooleanField(default=False)
    ecue_ignored = models.BooleanField()
    anuniv = models.ForeignKey(AnUniv, models.DO_NOTHING)
    niveau = models.ForeignKey(Niveau, models.DO_NOTHING)
    ue = models.ForeignKey(Ue, models.DO_NOTHING)
    afficher=models.BooleanField(null=True, default=False)
    report=models.BooleanField(null=True)
    calcmode=models.IntegerField(choices=calculs,null=True)
    nbetudiant=models.IntegerField(null=True,default=0)
    pourcreussite=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    reporter=models.BooleanField(null=True, default=False)
    idx=models.IntegerField(default=0, primary_key=False)
    nbtp=models.IntegerField(default=0,null=True)
    nbtd=models.IntegerField(default=0,null=True)
    nbcm=models.IntegerField(default=0,null=True)
    coefcm=models.IntegerField(default=1,null=True)
    coeftp=models.IntegerField(default=1,null=True)
    dcm=models.BooleanField(default=False,null=True)
    dtp=models.BooleanField(default=False,null=True)
    class Meta:
        db_table = 'examens'
        unique_together = (('anuniv', 'niveau', 'ue', 'session','id'),)
    def get_absolute_url(self):
        return reverse('detexam', args=[self.id])
    def __str__(self):
        return self.ue.code+' '+self.anuniv.labels
    



class Composition(models.Model):
    compid=models.BigIntegerField(default=0, primary_key=True)
    ano = models.BooleanField()
    fano = models.IntegerField(blank=True, null=True)
    lano = models.IntegerField(blank=True, null=True)
    compostdate = models.DateField(blank=True, null=True)
    coefficient = models.IntegerField(blank=True, null=True,default=1)
    ecue_ignored = models.BooleanField()
    comptype = models.ForeignKey(Compotype, models.DO_NOTHING)
    ecue = models.ForeignKey(UeInfo, models.DO_NOTHING)
    examen = models.ForeignKey(Examen, models.DO_NOTHING)
    reporter=models.BooleanField(null=True)
    effectif=models.IntegerField(default=1)
    session=models.IntegerField(default=1)
    exporter=models.BooleanField(default=False)
    genano=models.BooleanField(default=True,null=True,verbose_name="Générer")
    version=models.BooleanField(default=True,null=True,verbose_name="Version")
    tsave=models.BooleanField(default=False,null=True)
    class Meta:

        db_table = 'compositions'
        unique_together = (('examen', 'ecue', 'comptype'),)
    def save(self, *args, **kwargs):
        if self.comptype.id==1:
            self.coefficient=self.ecue.ue.niveau.coefcm
        if self.comptype.id==2:
            self.coefficient=self.ecue.ue.niveau.coeftd
        if self.comptype.id==3:
            self.coefficient=self.ecue.ue.niveau.coeftp
            self.ano=False
        if self.comptype.id==6:
            self.coefficient=self.ecue.ue.niveau.coeftd
        if self.comptype.id==7:
            self.coefficient=self.ecue.ue.niveau.coefcm


        super(Composition, self).save(*args, **kwargs)
    def __str__(self):
        return self.ecue.labels
  
class Link_cm_td(models.Model):
    composition = models.ForeignKey(Composition, models.DO_NOTHING)
    linked_td=models.ForeignKey(Composition, models.DO_NOTHING,related_name="linked_cm")
    class Meta:
        db_table = 'Link_cm_td'
        unique_together = (('composition', 'linked_td'),)

class Anonymat(models.Model):
    ano = models.IntegerField(primary_key=True)
    error = models.BooleanField(default=False)
    composition = models.ForeignKey(Composition, models.DO_NOTHING)
    etudiant = models.ForeignKey(Etudiant, models.DO_NOTHING, blank=True, null=True)
    reclamation=models.BooleanField(null=True)
    reporter=models.BooleanField(null=True, default=False)
    anuniv=models.ForeignKey(AnUniv,models.DO_NOTHING, blank=True, null=True)
    class Meta:
        db_table = 'anonymats'
        unique_together = (('composition', 'etudiant'),)

    def __str__(self):
        return str(self.ano)



class Enseignant(models.Model):
    nompren = models.CharField(max_length=254)
    email = models.CharField(max_length=254)
    contact = models.CharField(max_length=65)
    emploi = models.IntegerField()

    class Meta:
 
        db_table = 'enseignants'

class Ecueinfo(models.Model):
    horaire = models.IntegerField()
    enseignant = models.ForeignKey(Enseignant, models.DO_NOTHING, blank=True, null=True)
    enseignement = models.ForeignKey(Compotype, models.DO_NOTHING)
    uei = models.ForeignKey(UeInfo, models.DO_NOTHING)

    class Meta:

        db_table = 'ecueinfos'
        unique_together = (('uei', 'enseignement'),)


class Enseignement(models.Model):
    code = models.CharField(max_length=2)
    labels = models.CharField(max_length=25)
    coef = models.IntegerField()

    class Meta:

        db_table = 'enseignement'




class Heures(models.Model):
    cdate = models.DateField()
    debut = models.TimeField()
    fin = models.TimeField()
    anuniv = models.ForeignKey(AnUniv, models.DO_NOTHING)
    ecues = models.ForeignKey(Ecueinfo, models.DO_NOTHING)
    enseignant = models.ForeignKey(Enseignant, models.DO_NOTHING)
    enseignement = models.ForeignKey(Compotype, models.DO_NOTHING)
    niveau = models.ForeignKey(Niveau, models.DO_NOTHING)
    ue = models.ForeignKey(Ue, models.DO_NOTHING)

    class Meta:

        db_table = 'heures'

class UeOption(models.Model):
    code = models.CharField(max_length=6)
    labels = models.CharField(max_length=125)
    ue = models.ForeignKey(Ue, models.DO_NOTHING)

    class Meta:
        db_table = 'ue_options'



class Inscription(models.Model):
    statut = models.ForeignKey(Statut_info,models.DO_NOTHING,null=True)
    nban = models.IntegerField(blank=True, null=True)
    anuniv = models.ForeignKey(AnUniv, models.DO_NOTHING)
    etudiant = models.ForeignKey(Etudiant, models.DO_NOTHING)
    niveau = models.ForeignKey(Niveau, models.DO_NOTHING,null=True)
    cfc=models.BooleanField(default=False,null=True)
    inscrit=models.BooleanField(default=True,null=True)

    class Meta:
        db_table = 'inscriptions'
        unique_together = (('niveau', 'anuniv','etudiant'),)

  
    def __str__(self):
        return str(self.etudiant.nce)

class tmp_inscr(models.Model):
    statut = models.ForeignKey(Statut_info,models.DO_NOTHING,null=True)
    nban = models.IntegerField(blank=True, null=True)
    anuniv = models.ForeignKey(AnUniv, models.DO_NOTHING)
    etudiant = models.ForeignKey(Etudiant, models.DO_NOTHING,null=True)
    niveau = models.ForeignKey(Niveau, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'tmp_inscr'

    def get_absolute_url(self):
        return reverse('resultats', args=[self.etudiant])


class NoteInscription(models.Model):
    id = models.IntegerField(primary_key=True)
    statut = models.IntegerField(blank=True, null=True)
    anuniv = models.IntegerField()
    etudiant= models.IntegerField()
    niveau = models.IntegerField(blank=True, null=True)
    resstatut = models.IntegerField(blank=True, null=True)
    lniveau = models.IntegerField(blank=True, null=True)
    gcredit = models.DecimalField(max_digits=6, decimal_places=2)
    ncredit = models.DecimalField(max_digits=6, decimal_places=2)
    nban = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'note_inscription'

class Resultat_info(models.Model):
    labels = models.CharField(max_length=50)

    class Meta:
        db_table = 'resultat_infos'
    def __str__(self):
        return self.labels



class Resultat(models.Model):
    id = models.AutoField(primary_key=True)
    nban = models.IntegerField()
    statut = models.ForeignKey(Statut_info,models.DO_NOTHING,null=True)
    credit = models.IntegerField(null=True)
    toprint = models.BooleanField(blank=True, null=True)
    moyenne = models.FloatField(null=True)
    etudiant = models.ForeignKey(Etudiant, models.DO_NOTHING)
    maxan = models.ForeignKey(AnUniv, models.DO_NOTHING)
    niveau = models.ForeignKey(Niveau, models.DO_NOTHING)
    credit_aniveau=models.IntegerField(null=True)
    class Meta:
        db_table = 'resultat'
        unique_together = (('etudiant', 'maxan', 'niveau'),)
    def save(self, *args, **kwargs):
        if self.nban==1 and self.credit<48:
            self.statut.id=3
        if self.nban==1 and self.credit>=48 and self.credit<60:
            self.statut.id=2
        if self.credit==60:
            self.statut.id=1
        if self.nban>1 and self.credit<60:
            self.statut.id=4
        if self.credit>60:
            self.statut.id=5
        super(Resultat, self).save(*args, **kwargs)

class Notes_ecue(models.Model):
    coef = models.IntegerField()
    note = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    notepond = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    anonymat = models.ForeignKey(Anonymat, models.DO_NOTHING, blank=True, null=True)
    composition = models.ForeignKey(Composition, models.DO_NOTHING, blank=True, null=True)
    ecue = models.ForeignKey(UeInfo, models.DO_NOTHING)
    etudiant = models.ForeignKey(Etudiant, models.DO_NOTHING)
    examen = models.ForeignKey(Examen, models.DO_NOTHING)
    ue = models.ForeignKey(Ue, models.DO_NOTHING)
    reclamation=models.BooleanField(default=False,null=True)
    reclamdate=models.DateTimeField(null=True)
    reporter=models.BooleanField(null=True, default=False)
    version=models.CharField(max_length=1,null=True)
  
    class Meta:
        db_table = 'notes_ecues'
        unique_together = (('etudiant', 'examen', 'composition'),)

    def save(self, *args, **kwargs):
        self.examen=self.composition.examen
        self.ue=self.examen.ue
        if self.examen.afficher==True:
            self.reclamation=True
        self.ecue=self.composition.ecue
        if self.coef==None:
            self.coef=self.composition.coefficient
        if self.note<0:
            self.note=0
        self.notepond=self.note*self.coef
        super(Notes_ecue, self).save(*args, **kwargs)


class Note(models.Model):
    note=models.TextField()
    class Meta:
        db_table="journal"

class Notes_Ue(models.Model):
    moyenne = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    resultat = models.ForeignKey(Resultat_info, models.DO_NOTHING, null=True)
    moypond = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    credits = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    etudiant = models.ForeignKey(Etudiant, models.DO_NOTHING)
    examen = models.ForeignKey(Examen, models.DO_NOTHING)
    repeche = models.BooleanField(null=True)
    reclamation=models.BooleanField(null=True)
    fini=models.BooleanField(null=True, default=False)
    decompense=models.BooleanField(null=True, default=False)
    pvtire=models.BooleanField(default=False)
    modifdate=models.DateField(default=timezone.now,null=True)
    notes=models.ManyToManyField(Note,blank=True)
    utilisateur=CurrentUserField()
    class Meta:
        db_table = 'notes_ue'
        unique_together = (('etudiant', 'examen', 'resultat'),)
    @property

    def init_track_fields(self):
        return ('etudiant','examen','moyenne','resultat',)

    def add_track_save_note(self):
        field_track={}
        for field in self.init_track_fields:
            value = getattr(self, field)
            orig_value = getattr(self, '_original_%s' % field)
            if value != orig_value:
                field_track[field] = [orig_value, value]

        if field_track:
            note_str = 'Les valeurs suivantes ont été modifiée:<br /><br />'
            for k, v in field_track.items():
                note_str += ('<b>{field}:</b> <i>{orig_value}</i> '
                             '<b>&rarr;</b> {value}<br />').format(
                    field=k,
                    orig_value=v[0],
                    value=v[1],
                )
            note = Note.objects.create(note=note_str)
            self.notes.add(note)
            
    def save(self, *args, **kwargs):
        self.credits=self.examen.ue.credits
        self.moypond=self.moyenne*self.credits
        user=get_current_user()
        self.utilisateur=user
        add_track = bool(self.pk)
        super(Notes_Ue, self).save(*args, **kwargs)
        #if add_track:
            #self.add_track_save_note()



class Resultat_semestre(models.Model):
    sumid = models.AutoField(primary_key=True)
    semestre = models.IntegerField()
    moyenne = models.DecimalField(max_digits=6, decimal_places=2)
    anuniv = models.ForeignKey(AnUniv, models.DO_NOTHING)
    etudiant = models.ForeignKey(Etudiant, models.DO_NOTHING)
    niveau = models.ForeignKey(Niveau, models.DO_NOTHING)
    sumcredit=models.DecimalField(max_digits=6, decimal_places=2,null=True)

    class Meta:
        db_table = 'resultat_semestre'
        unique_together = (('etudiant', 'anuniv', 'niveau', 'semestre'),)


class Resultat_uecat(models.Model):
    sumid = models.IntegerField(primary_key=True)
    semestre = models.IntegerField()
    credit = models.IntegerField()
    moyenne = models.DecimalField(max_digits=6, decimal_places=2)
    statut = models.IntegerField(blank=True, null=True)
    anuniv = models.ForeignKey(AnUniv, models.DO_NOTHING)
    etudiant = models.ForeignKey(Etudiant, models.DO_NOTHING)
    niveau = models.ForeignKey(Niveau, models.DO_NOTHING)
    uecat = models.ForeignKey(UeCat, models.DO_NOTHING)

    class Meta:
        db_table = 'resultat_uecat_semestre'


class Resultat_bigcat(models.Model):
    bcid = models.AutoField(primary_key=True)
    semestre = models.IntegerField()
    credit = models.IntegerField()
    moyenne = models.DecimalField(max_digits=6, decimal_places=2)
    statut = models.IntegerField(blank=True, null=True)
    anuniv = models.ForeignKey(AnUniv, models.DO_NOTHING)
    etudiant = models.ForeignKey(Etudiant, models.DO_NOTHING)
    niveau = models.ForeignKey(Niveau, models.DO_NOTHING)
    nbueaj=models.IntegerField(default=0,null=True)
    biguecat = models.ForeignKey(BigUeCat, models.DO_NOTHING,null=True)
    credit=models.DecimalField(default=0,max_digits=6, decimal_places=2)
    credit_compens=models.DecimalField(default=0,max_digits=6, decimal_places=2)
    somme=models.DecimalField(max_digits=6, decimal_places=2,null=True)
    nbue7=models.IntegerField(default=0,null=True)
    pvtire=models.BooleanField(default=False)
    class Meta:
        db_table = 'resultat_bigcat_semestre'
        unique_together = (('etudiant', 'anuniv', 'niveau', 'semestre','biguecat'),)

class Salle(models.Model):
    nom = models.CharField(max_length=125)
    place = models.IntegerField()
    utiliser = models.BooleanField()
    dispach=models.BooleanField(default=False)
    class Meta:
        db_table = 'salles'

class tmpnote(models.Model):
    idtmp=models.AutoField(primary_key=True)
    nompren=models.CharField(max_length=125)
    composition=models.ForeignKey(Composition, models.DO_NOTHING)
    notes=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    etudiant=models.ForeignKey(Etudiant, models.DO_NOTHING, null=True)


class moyenne_ecue(models.Model):
    id=models.AutoField(primary_key=True)
    examen=models.ForeignKey(Examen,on_delete=models.DO_NOTHING)
    ecue=models.ForeignKey(UeInfo, on_delete=models.DO_NOTHING)
    coefficient=models.IntegerField(default=1)
    moyenne=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    etudiant=models.ForeignKey(Etudiant, on_delete=models.CASCADE,null=True)
    reclamation=models.BooleanField(null=True,default=False)
    class Meta:
        db_table = 'moyenne_ecue'

class moyenne_ecue_tmp(models.Model):
    id=models.AutoField(primary_key=True)
    examen=models.ForeignKey(Examen,on_delete=models.DO_NOTHING)
    ecue=models.ForeignKey(UeInfo, on_delete=models.DO_NOTHING)
    coefficient=models.IntegerField(default=1)
    moyenne=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    etudiant=models.ForeignKey(Etudiant, on_delete=models.CASCADE,null=True)

    class Meta:
        db_table = 'moyenne_ecue_tmp'

class Moyenne_ecue_cm(models.Model):
    id=models.AutoField(primary_key=True)
    composition=models.ForeignKey(Composition,on_delete=models.DO_NOTHING)
    examen=models.ForeignKey(Examen,on_delete=models.DO_NOTHING)
    sumcmtd=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    coefsum=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    moyenne=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    etudiant=models.ForeignKey(Etudiant, on_delete=models.CASCADE,null=True)
    coefcm=models.IntegerField(default=1)
    moypond=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    reclamation=models.BooleanField(null=True,default=False)
    class Meta:
        db_table = 'moyenne_ecue_cm'
        unique_together = (('etudiant', 'composition','examen'))
    def save(self, *args, **kwargs):
        self.moyenne=self.sumcmtd/self.coefsum
        self.coefcm=self.examen.coefcm
        self.moypond=self.coefcm*self.moyenne
        super(Moyenne_ecue_cm, self).save(*args, **kwargs)

class Moyenne_ue_cm(models.Model):
    id=models.AutoField(primary_key=True)
    examen=models.ForeignKey(Examen,on_delete=models.DO_NOTHING)
    sumcm=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    coefsum=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    moyenne=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    etudiant=models.ForeignKey(Etudiant, on_delete=models.CASCADE,null=True)
    coefcm=models.IntegerField(default=1)
    moypond=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    reclamation=models.BooleanField(null=True,default=False)
    class Meta:
        db_table = 'moyenne_ue_cm'
        unique_together = (('etudiant','examen'))
    def save(self, *args, **kwargs):
        self.moyenne=self.sumcm/self.coefsum
        self.coefcm=self.examen.coefcm
        self.moypond=self.coefcm*self.moyenne
        super(Moyenne_ue_cm, self).save(*args, **kwargs)

class Moyenne_ue_tp(models.Model):
    id=models.AutoField(primary_key=True)
    examen=models.ForeignKey(Examen,on_delete=models.DO_NOTHING)
    sumtp=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    coefsum=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    moyenne=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    etudiant=models.ForeignKey(Etudiant, on_delete=models.CASCADE,null=True)
    coeftp=models.IntegerField(default=1)
    moypond=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    reclamation=models.BooleanField(null=True,default=False)
    class Meta:
        db_table = 'moyenne_ue_tp'
        unique_together = (('etudiant','examen'))
    def save(self, *args, **kwargs):
        self.coeftp=self.examen.coeftp
        self.moyenne=self.sumtp/self.coefsum
        self.moypond=self.coeftp*self.moyenne
        super(Moyenne_ue_tp, self).save(*args, **kwargs)


class Moyenne_tmp_cmtp(models.Model):
    id=models.AutoField(primary_key=True)
    examen=models.ForeignKey(Examen,on_delete=models.DO_NOTHING)
    moyenne=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    coefficient=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    etudiant=models.ForeignKey(Etudiant, on_delete=models.CASCADE,null=True)
    moypond=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    comptype=models.ForeignKey(Compotype, on_delete=models.CASCADE, null=True)
    reclamation=models.BooleanField(null=True,default=False)

    class Meta:
        db_table = 'moyenne_tmp_cmtp'
        unique_together = (('etudiant','examen','comptype'))
    
    def save(self, *args, **kwargs):
        self.moypond=self.coefficient*self.moyenne
        super(Moyenne_tmp_cmtp, self).save(*args, **kwargs)

class Moyenne_Ue(models.Model):
    id=models.AutoField(primary_key=True)
    examen=models.ForeignKey(Examen,on_delete=models.DO_NOTHING)
    somme=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    coefficient=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    moyenne=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    etudiant=models.ForeignKey(Etudiant, on_delete=models.CASCADE,null=True)
    reclamation=models.BooleanField(null=True,default=False)
    
    class Meta:
        db_table = 'moyenne_ue'
        unique_together = (('etudiant','examen'))
    def save(self, *args, **kwargs):
        self.moyenne=self.somme/self.coefficient
        super(Moyenne_Ue, self).save(*args, **kwargs)

class Moyenne_ue_cmtp(models.Model):
    id=models.AutoField(primary_key=True)
    examen=models.ForeignKey(Examen,on_delete=models.DO_NOTHING)
    moyenne=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    comptype=models.ForeignKey(Compotype,on_delete=models.DO_NOTHING,null=True)
    etudiant=models.ForeignKey(Etudiant, on_delete=models.CASCADE,null=True)
    coefficient=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    moypond=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    reclamation=models.BooleanField(null=True,default=False)
    resultat = models.ForeignKey(Resultat_info, models.DO_NOTHING, null=True,related_name="resultat")
    
    class Meta:
        db_table = 'moyenne_ue_cmtp'
        unique_together = (('etudiant', 'examen','comptype'))
    def save(self, *args, **kwargs):
        self.moypond=self.moyenne*self.coefficient
        super(moyenne_ue_cmtp, self).save(*args, **kwargs)


class Resultat_examen_cmtp(models.Model):
    id=models.AutoField(primary_key=True)
    examen=models.ForeignKey(Examen,on_delete=models.DO_NOTHING)
    etudiant=models.ForeignKey(Etudiant, on_delete=models.CASCADE,null=True)
    res_cm = models.ForeignKey(Resultat_info,models.DO_NOTHING,null=True,related_name="res_cm")
    res_tp = models.ForeignKey(Resultat_info,models.DO_NOTHING,null=True,related_name="res_tp")
    resultat=models.ForeignKey(Resultat_info,models.DO_NOTHING,null=True,related_name="resultat_cmtp")

    class Meta:
        db_table = 'resultat_examen_cmtp'
        unique_together = (('etudiant', 'examen',))

class Historic(models.Model):
    semestre = models.IntegerField()
    statut = models.IntegerField()
    moyenne = models.DecimalField(max_digits=6, decimal_places=2)
    credit = models.DecimalField(max_digits=4, decimal_places=2)
    moypond = models.DecimalField(max_digits=6, decimal_places=2)
    exams = models.IntegerField()
    au = models.ForeignKey(AnUniv, models.DO_NOTHING)
    etudiant = models.ForeignKey(Etudiant, models.DO_NOTHING)
    niveau = models.ForeignKey(Niveau, models.DO_NOTHING)
    resultat = models.ForeignKey(Resultat, models.DO_NOTHING, blank=True, null=True)
    ue = models.ForeignKey(Ue, models.DO_NOTHING)
    uecat = models.ForeignKey(UeCat, models.DO_NOTHING)

    class Meta:
        db_table = 'historique'
        unique_together = (('etudiant', 'au', 'niveau', 'ue', 'statut'),)

class NoteHistoric(models.Model):
    id = models.IntegerField(primary_key=True)
    semestre = models.IntegerField()
    statut = models.ForeignKey(Resultat_info,models.DO_NOTHING)
    moyenne = models.DecimalField(max_digits=6, decimal_places=2)
    credit = models.DecimalField(max_digits=4, decimal_places=2)
    moypond = models.DecimalField(max_digits=6, decimal_places=2)
    au_id = models.IntegerField()
    etudiant_id = models.IntegerField()
    niveau_id = models.IntegerField()
    ue_id = models.IntegerField()
    uecat_id = models.IntegerField()
    resultat_id = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'note_historic'

class suspension(models.Model):
    id = models.IntegerField(primary_key=True)
    etudiant=models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    anuniv = models.ForeignKey(AnUniv, models.DO_NOTHING)

    class Meta:
        db_table = 'suspension'


class equivalence(models.Model):
    ue_from=models.ForeignKey(Ue,on_delete=models.DO_NOTHING,related_name="ue_from")
    ue_to=models.ForeignKey(Ue,on_delete=models.DO_NOTHING,related_name="ue_to")
    class Meta:
        db_table = 'equivalence_ue'


class Anonymat_x(models.Model):
    ano=models.IntegerField(null=False)
    etudiant=models.ForeignKey(Etudiant,on_delete=models.DO_NOTHING)
    composition=models.ForeignKey(Composition,on_delete=models.DO_NOTHING)
    class Meta:
        db_table = 'anonymat_x'


class err_inscription(models.Model):
    statut = models.ForeignKey(Statut_info,models.DO_NOTHING,null=True)
    nban = models.IntegerField(blank=True, null=True)
    anuniv = models.ForeignKey(AnUniv, models.DO_NOTHING)
    etudiant = models.ForeignKey(Etudiant, models.DO_NOTHING,null=True)
    niveau = models.ForeignKey(Niveau, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'inscr_erreur'


class anotmp(models.Model):
    etudiant=models.ForeignKey(Etudiant,models.DO_NOTHING)
    rang=models.IntegerField()
    ano=models.IntegerField(null=True)

    class Meta:
        db_table = 'anotmp'


class authorization(models.Model):
    login=models.CharField(max_length=12)
    password=models.CharField(max_length=15)
    habilitation=models.IntegerField(default=1)
    class Meta:
        db_table="authorization"



class Note_journal(models.Model):
    note=models.TextField()
    class Meta:
        db_table="journal_note"

class TimeLog(models.Model):
    time_spent=models.DecimalField(max_digits=4,decimal_places=2)
    note=models.ManyToManyField(Note,blank=True)
    @property
    def init_track_fields(self):
        return ('time_spent',)
    

    def add_track_save_note(self):
        field_track={}
        for field in self.init_track_fields:
            value = getattr(self, field)
            orig_value = getattr(self, '_original_%s' % field)
            if value != orig_value:
                field_track[field] = [orig_value, value]

        if field_track:
            note_str = 'Les champs suivants ont été modifiés:<br /><br />'
            for k, v in field_track.iteritems():
                note_str += ('<b>{field}:</b> <i>{orig_value}</i> '
                             '<b>&rarr;</b> {value}<br />').format(
                    field=k,
                    orig_value=v[0],
                    value=v[1],
                )

            note = Note.objects.create(note=note_str)
            self.notes.add(note)
    def save(self, *args, **kwargs):
        add_track = bool(self.pk)
        super(TimeLog, self).save(*args, **kwargs)

        if add_track:
            self.add_track_save_note()
def timelog_post_init(sender, instance, **kwargs):
        if instance.pk:
            for field in instance.init_track_fields:
                setattr(instance, '_original_%s' % field, getattr(instance, field))
post_init.connect(
    timelog_post_init,
    sender=Notes_Ue
)


class Dispaching(models.Model):
    etudiant=models.ForeignKey(Etudiant,models.DO_NOTHING)
    rang=models.IntegerField()
    salle=models.ForeignKey(Salle,on_delete=models.DO_NOTHING,null=True)
    examen=models.ForeignKey(Examen,on_delete=models.DO_NOTHING,null=True)
    class Meta:
        db_table = 'dispaching'