$('#filename').click((event) => {
	event.target.value = null;
});

$('#filename').change((event) => {

	var reader = new FileReader();

	reader.onload = () => {

		var getByCol = function(array, columns, colName) {
			var index = columns.indexOf(colName);

			if(index == -1)
				return false;

			return array[index] != '' ? array[index] : false;
		}

		var setByCol = function(array, columns, colName, value) {
			var index = columns.indexOf(colName);

			if(index == -1)
				return false;

			if(value === false)
				value = '';

			array[index] = value;

			return true;
		}

		var filter = function(array, map) {
			var filteredArray = [];

			for(var i=0; i<map.length; ++i)
				filteredArray.push(array[map[i]]);

			return filteredArray;
		}

		var filterInv = function(array, map) {
			map.slice(0).sort(function(a,b){ return b - a; });
			array = array.slice(0);

			for(var i=map.length -1; i >= 0; --i)
				array.splice(map[i], 1);

			return array;
		}

		var getMap = function(array, selectionFct) {
			var map = [];

			array.forEach((elt, index, arr) => {
				if(selectionFct(elt, index, arr))
					map.push(index);
			});

			return map;
		}


		var input = reader.result.replace(/\r/g, '').split('\n').filter((l) => {
			return l != '';
		});
		var columns = input.shift().split(';');
		var columnsMap = getMap(columns, (column) => {
			return column != '';
		});

		columns = filter(columns, columnsMap);

		columns.push("type");
		columns.push("mmm_new");

		var columnsMapPost = getMap(columns, (column) => {
			return column.indexOf('post_') == 0;
		});

		var partners = '';

		partners += filterInv(columns, columnsMapPost).join(';') + '\n';

		input.forEach((values) => {

			values = values.split(';');
			values = filter(values, columnsMap);
			//values.push(true);
			setByCol(values, columns, 'type', 'contact');
			setByCol(values, columns, 'mmm_new', true);

			partners += filterInv(values, columnsMapPost).join(';') + '\n';

			if(getByCol(values, columns, 'post_street')) {

				setByCol(values, columns, 'type', 'invoice');
				setByCol(values, columns, 'mmm_new', false);

				setByCol(values, columns, 'supplier', false);
				setByCol(values, columns, 'customer', false);
				setByCol(values, columns, 'state', '');
				setByCol(values, columns, 'sector_id', false);
				setByCol(values, columns, 'parent_id', getByCol(values, columns, 'name'));
				setByCol(values, columns, 'vat', false);
				setByCol(values, columns, 'phone', false);
				setByCol(values, columns, 'website', false);
				setByCol(values, columns, 'email', false);
				setByCol(values, columns, 'street', getByCol(values, columns, 'post_street'));
				setByCol(values, columns, 'street2', getByCol(values, columns, 'post_street2'));
				setByCol(values, columns, 'zip', getByCol(values, columns, 'post_zip'));
				setByCol(values, columns, 'city', getByCol(values, columns, 'post_city'));
				setByCol(values, columns, 'country_id', getByCol(values, columns, 'post_country_id'));
				setByCol(values, columns, 'user_id', false);
				setByCol(values, columns, 'title', false);
				setByCol(values, columns, 'name', getByCol(values, columns, 'name') + ' - Facturation');
				setByCol(values, columns, 'lang', false);
				setByCol(values, columns, 'function', false);
				setByCol(values, columns, 'mobile', false);
				setByCol(values, columns, 'invitation_ids', false);

				partners += filterInv(values, columnsMapPost).join(';') + '\n';
			}
		});

		$('#partners').text(partners);
	};

	reader.readAsText(event.target.files[0]);
});