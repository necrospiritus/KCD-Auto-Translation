# KCD-Auto-Translation
[![GitHub issues](https://img.shields.io/github/issues/necrospiritus/KCD-Auto-Translation?style=plastic)](https://github.com/necrospiritus/KCD-Auto-Translation/issues)
[![GitHub stars](https://img.shields.io/github/stars/necrospiritus/KCD-Auto-Translation?style=plastic)](https://github.com/necrospiritus/KCD-Auto-Translation/stargazers)
![GitHub repo size](https://img.shields.io/github/repo-size/necrospiritus/KCD-Auto-Translation?style=plastic)
![GitHub](https://img.shields.io/github/license/necrospiritus/KCD-Auto-Translation?style=plastic)

This program sends localization .xml files of Kingdom Come Deliverance to Google Translate for auto translation.

## Purpose

There is two options for using this program:

1-You can auto-translate missing translation in available game languages.

2-You can auto-translate to a new language from available game languages.

Avaible game languages:

cs-**Czech**
en-**English**
et-**Estonian**
fr-**French**
de-**German**
it-**Italian**
pl-**Polish**
ru-**Russian**
es-**Spanish**
tr-**Turkish**
uk-**Ukrainian**

## Logic of Program

Program runs in six steps.

**STEP 1**: Checks File Compatibility

	Basicly counts begining and ending of elements and compares with each other. XML structure: 
	
	<Table>
		<Row>
			<Cell>text id</Cell>
			<Cell>original english text</Cell>
			<Cell>original transleted text</Cell>
		</Row>
	</Table>

**STEP 2**: Parsing XMl file and transferring texts in 'Cell' element to Database.
	Database structure:
	<table>
		<thead>
		<tr>
			<th>row</th>
			<th>cell</th>
			<th>text</th>
		</tr>
		</thead>
		<tbody>
		<tr>
			<td>&nbsp;1</td>
			<td>ID</td>
			<td>text id</td>
		</tr>
		<tr>
			<td>&nbsp;1</td>
			<td>ORIGINAL</td>
			<td>original english text</td>
		</tr>
		<tr>
			<td>&nbsp;1</td>
			<td>TRANSLATE</td>
			<td>original&nbsp;transleted text</td>
		</tr>
		<tr>
			<td>&nbsp;1</td>
			<td>NEW TRANSLATION</td>
			<td>auto-transleted text</td>
		</tr>
		<tr>
			<td>&nbsp;2</td>
			<td>ID</td>
			<td>&nbsp;ui_nh_res_stone</td>
		</tr>
		<tr>
			<td>&nbsp;2</td>
			<td>ORIGINAL</td>
			<td>&nbsp;Stone</td>
		</tr>
		<tr>
			<td>&nbsp;2</td>
			<td>TRANSLATE</td>
			<td>&nbsp;Stone</td>
		</tr>
		<tr>
			<td>&nbsp;2</td>
			<td>NEW TRANSLATION</td>
			<td>&nbsp;Taş</td>
		</tr>
		<tr>
			<td>&nbsp;...</td>
			<td>&nbsp;...</td>
			<td>&nbsp;...</td>
		</tr>
		<tbody>
	</table>

**STEP 3**: Preparing For Translate

Each texts collects in pieces of 10k characters with using of string or list variables depending on purpose.

**STEP 4**: Transferring text to Google and retrieving translated texts.

**STEP 5**: Adding translated texts to database.

**STEP 6**: Creating a new XML file.
## Requirement

google-trans = https://github.com/ssut/py-googletrans

```
googletrans>=2.4.0
```

## Built With

* [PyCharm](https://www.jetbrains.com/pycharm/) - The Python IDE

## Authors

* **Burak Karabey** - *Initial work* - [necrospiritus](https://github.com/necrospiritus)

## License

This project is licensed under the GPL-2.0 License - see the [LICENSE.md](LICENSE.md) file for details



