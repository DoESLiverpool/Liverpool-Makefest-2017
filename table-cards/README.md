# Table Cards

Generate table cards from a spreadsheet and an svg template.

The ods file is a download from [a google spreadsheet](https://docs.google.com/spreadsheets/d/1Shh42EFP3nMiW4gl09GxYrjqYToIDtuDAYZKMEBPNic/edit?usp=sharing).
Entries can be added directly from the associated [google form](https://goo.gl/forms/ZycuK1ryiiZRvH8O2).

## Usage

Run:

```
./cardgen.py
```

or for more options:

```
./cardgen.py -h
```

## Requires

 * python (tested on python3) — although it should only use default installed libraries,
 * libreoffice calc; to convert spreadsheets to csv
 * inkscape; to convert svg to pdfs,
 * pdftk; to concatenate all the pdfs into one file for printing.
