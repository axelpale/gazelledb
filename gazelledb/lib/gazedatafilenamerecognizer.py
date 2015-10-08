import re
import os

class GazedataFilenameRecognizer(object):

	# Pattern of gazefile filenames
	__fileregexp = 'cg(\d+)_(\d+[a-z]?)_childcogn_(\d)m(NoCalib)?_SRT(\d)'
	__patt = re.compile(__fileregexp)

	def recognize_from_filename(self, file):
		# Recognize metadata from filename
		bn = os.path.basename(file)
		m = self.__patt.match(bn)
		return {
			'participant_id': m.group(1).zfill(4),
			'method_version': m.group(2),
			'participant_age_months': int(m.group(3)),
			'calibration_successful': (m.group(4) == None),
			'trial_configuration_id': 'SRT' + m.group(5)
		}
