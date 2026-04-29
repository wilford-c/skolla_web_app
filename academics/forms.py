from django import forms

from students.models import Student

from .models import Assessment, Classroom, Grade, Subject


class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['name', 'code', 'homeroom_teacher', 'description']


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'classroom', 'teacher', 'weekly_sessions']


class AssessmentForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = Assessment
        fields = [
            'name',
            'subject',
            'assessment_type',
            'max_score',
            'weight',
            'date',
            'description',
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add helpful placeholders
        self.fields['name'].widget.attrs['placeholder'] = 'e.g., Midterm Exam, Chapter 3 Quiz'
        self.fields['max_score'].widget.attrs['placeholder'] = '100.00'
        self.fields['weight'].widget.attrs['placeholder'] = '10.00'


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['student', 'assessment', 'score', 'remarks']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add helptext for score field
        if self.instance and self.instance.assessment:
            max_score = self.instance.assessment.max_score
            self.fields['score'].help_text = f'Maximum score: {max_score}'
        
        # Order students by admission number
        self.fields['student'].queryset = Student.objects.filter(
            status=Student.Status.ACTIVE
        ).order_by('admission_number')
    
    def clean_score(self):
        score = self.cleaned_data.get('score')
        assessment = self.cleaned_data.get('assessment')
        
        if score and assessment and score > assessment.max_score:
            raise forms.ValidationError(
                f'Score ({score}) cannot exceed maximum score ({assessment.max_score})'
            )
        
        return score


class BulkGradeForm(forms.Form):
    """Form for entering grades for multiple students at once."""
    
    assessment = forms.ModelChoiceField(
        queryset=Assessment.objects.all().select_related('subject'),
        empty_label='Select an assessment',
    )
    
    def __init__(self, *args, **kwargs):
        subject = kwargs.pop('subject', None)
        super().__init__(*args, **kwargs)
        
        if subject:
            self.fields['assessment'].queryset = Assessment.objects.filter(
                subject=subject
            ).select_related('subject')
        
        # Order assessments by date (most recent first)
        self.fields['assessment'].queryset = (
            self.fields['assessment'].queryset.order_by('-date')
        )
