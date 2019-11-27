from django.contrib import admin

from .models import Question, Choice


# admin.StackedInline would be similar to one column
class ChoiceInLine(admin.TabularInline):
    model = Choice
    # extra defines the extra slots
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    # first parameter: field title
    fieldsets = [
        (None, {'fields': ['questions_text']}),
        ('Date information', {'fields': ['publication_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInLine]

    # Options for the Questions base overview /admin/trees/question/
    # NOTE: without list_display set, admin page will fallback to __str__ in model
    list_display = ('questions_text', 'publication_date', 'was_published_recently')


admin.site.register(Question, QuestionAdmin)
