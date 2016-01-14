do
	local value = 0
	local last_update = 0

	function update_data()
		local now = os.time()

		if now <= last_update then
			return
		end

		local f = io.open("/tmp/router_status", "r")
		if f then
			v = f:read("*number")
			f:close()
			if v then
				value = v
			else
				value = -1
			end
		else
			value = 0
		end
	end

	function conky_router_ping()
		update_data()
		if value >= 0 then
			return value
		else
			return -100
		end
	end

	function conky_router_ping_string()
		update_data()
		if value >= 0 then
			return "${color0}" .. tostring(value) .. " ms"
		else
			return "${color red}lost"
		end
	end
end
