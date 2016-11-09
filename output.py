import fieldmap
import yaml
import csv
from exceptions import NegSampleSizeException
from randomcontact import RandomContact
from filelinks import output_file


class Output:

    @classmethod
    def save(self, no_of_people, output_filename, output_filetype='django_yaml_fixture',
        yaml_entity='Customer', id_start=1, id_step=1):
        """compile a list of people and save to a file"""
        if no_of_people <= 0:
            raise NegSampleSizeException("Can't generate zero or negative sample sizes! (n = %d)" % (no_of_people))
        contact = RandomContact.contact()
        with open(output_filename, "wb") as outputfile:
            new_contact = next(contact())
            # swallow empty first instance
            dontuse = list(next(new_contact).keys())
            if output_filetype == 'csv':
                wtr = self.setup_csv(outputfile)
            person_id = id_start
            for i in range(no_of_people):
                if output_filetype == 'csv':
                    p = fieldmap.translateOut(next(new_contact))
                    wtr.writerow(p)
                elif output_filetype == 'django_yaml_fixture':
                    p = fieldmap.translateOut(next(new_contact))
                    # print('map', p)
                    outputfile.write(
                        yaml.dump([{'model': yaml_entity,
                                    'pk': person_id,
                                    'fields': p}
                                   ]
                                  )
                    )
                person_id += id_step

    @classmethod
    def setup_csv(self, outputfile):
        # Write heading row in order of original contacts table
        # todo-nm outgoing translations passim
        # print("fieldorder", self.fieldorder)
        field_header = [fieldmap.OUTGOING_TRANSLATION[r]
                        for r
                        in self.fieldorder
                        if fieldmap.OUTGOING_TRANSLATION[r]]
        wtr = csv.DictWriter(outputfile, field_header, extrasaction='ignore')
        wtr.writeheader()
        return wtr


# todo optional primary key, currently only implemented for YAML fixture

if __name__ == "__main__":
    """
    generate a file, size no_of_people, list some names or dump all generated data to console
    """
    no_of_people = 50
    Output().save(no_of_people, output_filename=output_file("testing.csv"),
                  output_filetype='csv')
    Output().save(no_of_people, output_filename=output_file("testing.yaml"),
                  output_filetype='django_yaml_fixture',
                  yaml_entity='harv2.Customer')
