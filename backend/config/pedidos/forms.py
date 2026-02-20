from django import forms
from .models import DireccionEnvio, Pedido

#Regiosnes de Chile

REGIONES_CHILE = [
    ('Región de Arica y Parinacota', 'Región de Arica y Parinacota'),
    ('Región de Tarapacá', 'Región de Tarapacá'),
    ('Región de Antofagasta', 'Región de Antofagasta'),
    ('Región de Atacama', 'Región de Atacama'),
    ('Región de Coquimbo', 'Región de Coquimbo'),
    ('Región de Valparaíso', 'Región de Valparaíso'),
    ('Región Metropolitana', 'Región Metropolitana'),
    ('Región del Libertador General Bernardo O\'Higgins', 'Región de O\'Higgins'),
    ('Región del Maule', 'Región del Maule'),
    ('Región de Ñuble', 'Región de Ñuble'),
    ('Región del Biobío', 'Región del Biobío'),
    ('Región de La Araucanía', 'Región de La Araucanía'),
    ('Región de Los Ríos', 'Región de Los Ríos'),
    ('Región de Los Lagos', 'Región de Los Lagos'),
    ('Región de Aysén', 'Región de Aysén'),
    ('Región de Magallanes', 'Región de Magallanes'),
]

class DireccionEnvioForm(forms.ModelForm):
    region = forms.ChoiceField(
        choices=REGIONES_CHILE,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = DireccionEnvio
        fields = ['nombre_completo', 'telefono', 'direccion', 'referencia', 'comuna',
                  'region', 'codigo_postal', 'predeterminada']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'class' : 'form-control',
                'placeholder' : 'Nombre completo'
            }),

            'telefono': forms.TextInput(attrs={
                'class' : 'form-control',
                'placeholder' : '+56 9 1234 5678'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calle y número'
            }),
            'referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Depto, block, etc. (opcional)'
            }),
            'comuna': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Comuna'
            }),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código Postal (opcional)'
            }),
            'predeterminada': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

class CheckoutForm(forms.Form):
    # Dirección de envío
    usar_direccion_guardada = forms.BooleanField(required=False, initial=False)
    direccion_id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    nombre_completo = forms.CharField(max_length=200, required=False)
    telefono = forms.CharField(max_length=20, required=False)
    direccion = forms.CharField(max_length=255, required=False)
    referencia = forms.CharField(max_length=255, required=False)
    comuna = forms.CharField(max_length=100, required=False)
    region = forms.ChoiceField(choices=REGIONES_CHILE, required=False)
    codigo_postal = forms.CharField(max_length=10, required=False)
    
    # Método de pago
    metodo_pago = forms.ChoiceField(
        choices=Pedido.METODO_PAGO_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )

    # Notas adicionales
    notas = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Notas adicionales (opcional)'}),
        required=False
    )

    # Guardar dirección 

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

        # Agregar class CSS
        for field_name, field in self.fields.items():
            if field_name not in ['usar_direccion_guardada', 'metodo_pago']:
                field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        usar_guardada = cleaned_data.get('usar_direccion_guardada')

        # Si np usa dirección guardada, validar campos requeridos
        if not usar_guardada:
            required_fields = ['nombre_completo', 'telefono', 'direccion', 'comuna', 'region']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'Este campo es obligatorio.')

        return cleaned_data                


