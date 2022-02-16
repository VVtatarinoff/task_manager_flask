from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, DataRequired, Regexp


class CreateTag(FlaskForm):
    name = StringField('Name: #',
                       validators=[Length(max=20),
                                   DataRequired(),
                                   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Name must have only letters, '
                                          'numbers, dots or underscores')])
    description = StringField('Description: ',
                              validators=[Length(max=200)])
    submit = SubmitField('Create')


class EditTagForm(FlaskForm):
    name = StringField('Name: #',
                       validators=[Length(max=20),
                                   DataRequired(),
                                   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Name must have only letters, '
                                          'numbers, dots or underscores')])
    description = StringField('Description: ',
                              validators=[Length(max=200)])
    submit = SubmitField('Submit')

    def __init__(self, tag, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name.data = self.name.data or tag.name
        self.description.data = self.description.data or tag.description
        self.tag = tag
