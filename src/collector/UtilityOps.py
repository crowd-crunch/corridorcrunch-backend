
class UtilityOps:
	@staticmethod
	def GetClientIP(request):
		try:
			x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
			if x_forwarded_for:
				ip = x_forwarded_for.split(',')[0]
			else:
				ip = request.META.get('REMOTE_ADDR')
			return ip
		except Exception:
			return None


	@staticmethod
	def GetDictValues(dict, key, default):
		if dict and key in dict:
			return dict[key]
		return default


