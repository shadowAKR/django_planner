import logging

from django.db import models
from django.utils import timezone
from django.db.models.constants import LOOKUP_SEP
from django.db.models.query import QuerySet, Prefetch

logger = logging.getLogger(__name__)


class SoftDeletionManager(models.Manager):
    """
    Manager class for SoftDeletion
    """
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop("alive_only", True)
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return SoftDeletionQuerySet(self.model).filter(deleted_at=None)
        return SoftDeletionQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()



class SoftDeletionQuerySet(QuerySet):
    """
    Class that define actions on queryset for SoftDeletion
    """
    def delete(self, user=None):
        return super(SoftDeletionQuerySet, self).update(
            deleted_at=timezone.now(),
            deleted_by=user,
        )

    def hard_delete(self):
        return super(SoftDeletionQuerySet, self).delete()

    def alive(self):
        return self.filter(deleted_at=None)

    def dead(self):
        return self.exclude(deleted_at=None)

    def _filter_or_exclude_(self, *args, **kwargs):
        return super(SoftDeletionQuerySet, self).filter(*args, **kwargs)

    def select_related(self, *fields, filter_deleted=True):
        """
        Return a new QuerySet instance that will select related objects.

        If fields are specified, they must be ForeignKey fields and only those
        related objects are included in the selection.

        If select_related(None) is called, clear the list.
        """
        self._not_support_combined_queries("select_related")
        if self._fields is not None:
            raise TypeError(
                "Cannot call select_related() after .values() or .values_list()"
            )

        obj = self._chain()
        if fields == (None,):
            obj.query.select_related = False
        elif fields:
            obj.query.add_select_related(fields)
        else:
            obj.query.select_related = True
        if not filter_deleted or obj.query.select_related is False:
            return obj
        for field in fields:
            obj = obj.filter(**{f"{field}__deleted_at": None})
        return obj

    def prefetch_related(self, *lookups, filter_deleted=True):
        """
        Return a new QuerySet instance that will prefetch the specified
        Many-To-One and Many-To-Many related objects when the QuerySet is
        evaluated.

        When prefetch_related() is called more than once, append to the list of
        prefetch lookups. If prefetch_related(None) is called, clear the list.
        """
        excluded_models = ["CustomRecord"]
        clone = self._chain()
        if lookups == (None,):
            clone._prefetch_related_lookups = ()
        else:
            for lookup in lookups:
                if isinstance(lookup, Prefetch):
                    lookup = lookup.prefetch_to
                lookup = lookup.split(LOOKUP_SEP, 1)[0]
                if lookup in self.query._filtered_relations:
                    raise ValueError(
                        "prefetch_related() is not supported with FilteredRelation."
                    )
                lookup_type = type(getattr(self.model, lookup)).__name__
                if (
                    not (
                        self.model.__name__ in excluded_models
                        and lookup_type in ("GenericForeignKey", "SourceGM2MDescriptor")
                    )
                    and filter_deleted
                ):
                    clone = clone.filter(**{f"{lookup}__deleted_at": None})
            clone._prefetch_related_lookups = clone._prefetch_related_lookups + lookups
        return clone
