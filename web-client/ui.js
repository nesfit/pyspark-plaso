let hdfsPath = '/';
//hdfsPath = '/test_data/docker/';
let client = new ApiClient();

let showFileList = function(list, hdfsPath) {
	// convert to structured lists
	const dirs = new Set();
	const files = new Set();
	list.forEach(pathstr => {
		//parse path and name
		let path = '';
		let fname = '';
		let isdir = false;

		let i = pathstr.lastIndexOf('/');
		//recognize directories
		if (i !== -1 && i > 1 && i === pathstr.length - 1) {
			isdir = true;
			pathstr = pathstr.substring(0, pathstr.length - 1);
			i = pathstr.lastIndexOf('/');
		}
		//split
		if (i === -1) {
			path = '/';
			fname = pathstr;
		} else {
			path = pathstr.substring(0, i + 1);
			fname = pathstr.substring(i + 1);
		}
		//store
		if (path == hdfsPath) {
			if (isdir) {
				dirs.add(fname);
			} else {
				files.add(fname);
			}
		}
	});
	// fill the tables
	const dirList = Array.from(dirs).sort();
	const dirTable = $('#dirList');
	dirTable.empty();
	addDirRow(dirTable, '..', hdfsPath);
	dirList.forEach((item) => {
		addDirRow(dirTable, item, hdfsPath);
	});
	const fileList = Array.from(files).sort();
	const fileTable = $('#fileList');
	fileTable.empty();
	fileList.forEach((item) => {
		addFileRow(fileTable, item, hdfsPath);
	});
	feather.replace();
};

let addDirRow = function(parent, name, hdfsPath) {
	//dir link
	const row = $('<tr></tr>');
	const link = $('<a href="#"></a>').text(name);
	const destDir = concatPath(hdfsPath, name);
	link.click(() => {
		chdir(destDir);
		return false;
	});
	row.append($('<td></td>').append(link));
	//actions
	const acell = $('<td class="a"></td>');
	if (name != '..') {
		const zlink = $('<a href="#" title="download zip" class=""></a>').append($('<i data-feather="package"></i>'));
		zlink.click(() => {
			getZip(destDir);
			return false;
		});
		const dlink = $('<a href="#" title="delete" class="text-danger"></a>').append($('<i data-feather="trash-2">'));
		dlink.click(() => {
			if (window.confirm('Are you sure to delete directory ' + destDir + '?')) {
				rmdir(destDir);
			}
			return false;
		});
		acell.append(zlink, dlink);
	}
	row.append(acell);
	parent.append(row);
};

let addFileRow = function(parent, name, hdfsPath) {
	//dir link
	const row = $('<tr></tr>');
	const destFile = hdfsPath + name;
	row.append($('<td></td>').text(name));
	//actions
	const acell = $('<td class="a"></td>');
	if (name != '..') {
		const zlink = $('<a href="#" title="download" class="text-primary"></a>').append($('<i data-feather="download"></i>'));
		zlink.click(() => {
			getFile(destFile);
			return false;
		});
		const dlink = $('<a href="#" title="delete" class="text-danger"></a>').append($('<i data-feather="trash-2">'));
		dlink.click(() => {
			if (window.confirm('Are you sure to delete file ' + destFile + '?')) {
				rm(destFile);
			}
			return false;
		});
		acell.append(zlink, dlink);
	}
	row.append(acell);
	parent.append(row);
};

let refresh = function(hdfsPath) {
	client.getLs(hdfsPath).then((list) => {
		showFileList(list, hdfsPath);
	});
};

//======================================================================================
// Navigation actions

let chdir = function(hdfsPath) {
	console.log('chdir ' + hdfsPath);
	if (!hdfsPath.endsWith('/')) {
		hdfsPath += '/';
	}
	$('#inputCurPath').val(hdfsPath);
	refresh(hdfsPath);
};

let rmdir = function(destDir) {
	console.log('rmdir ' + destDir);
	client.rmdir(destDir);
	refresh(getCwd());
}

let rm = function(destFile) {
	console.log('rm ' + destFile);
	client.rm(destFile);
	refresh(getCwd());
}

let getZip = function(path) {
	console.log('getZip ' + path);
	window.open(client.zipLink(path), '_blank');
};

let getFile = function(path) {
	window.open(client.fileLink(path), '_blank');
};

let runExtraction = function(path) {
	window.open(client.extractLink(path), '_blank');
};

//======================================================================================
// Utils

let concatPath = function(base, name) {
	if (name == '..') {
		if (base.length > 1) {
			let path = base.substring(0, base.length - 1);
			const i = path.lastIndexOf('/');
			if (i !== -1) {
				path = path.substring(0, i + 1);
			}
			return path;
		} else {
			return base;
		}
	} else {
		return base + name + '/';
	}
};

let getCwd = function() {
	let cwd = $('#inputCurPath').val();
	if (!cwd.endsWith('/')) {
		cwd += '/';
		$('#inputCurPath').val(cwd);
	}
	return cwd;
};

let showMsg = function(dest, type, text) {
	dest.empty();
	dest.append($('<div class="alert" role="alert"></div>').addClass(type).text(text));
	setTimeout(function() {
		dest.empty();
	}, 5000);
};

//======================================================================================

$(function(){

	$('#inputCurPath').val(hdfsPath);
	$('#curPathSubmit').click(function() {
		refresh(getCwd());
		return false;
	});

	$('#buttonMkdir').click(function() {
		var dirname = $('#inputMkdir').val();
		if (!dirname.endsWith('/')) {
			dirname += '/';
		}
		client.mkdir(getCwd(), dirname);
		refresh(getCwd());
		showMsg($('#messagesMkdir'), 'alert-success', 'Folder created');
	});

	$('#buttonUploadFile').click(function() {
		const files = document.getElementById('inputUploadFile').files;
		client.uploadFile(getCwd(), files[0])
			.then(msg => {
				console.log(msg);
				showMsg($('#messagesUploadFile'), 'alert-success', msg);
				refresh(getCwd());
			})
			.catch(error => {
				console.error(error)
				showMsg($('#messagesUploadFile'), 'alert-error', error);
			})
	});

	$('#buttonUploadZip').click(function() {
		const files = document.getElementById('inputUploadZip').files;
		client.uploadZip(getCwd(), files[0])
			.then(msg => {
				console.log(msg);
				showMsg($('#messagesUploadZip'), 'alert-success', msg);
				refresh(getCwd());
			})
			.catch(error => {
				console.error(error)
				showMsg($('#messagesUploadZip'), 'alert-error', error);
			})
	});

	$('#buttonExec').click(function() {
		runExtraction(getCwd());
	});

	refresh(hdfsPath);

});
