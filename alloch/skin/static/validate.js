/*

Permet de vérifier tous les formulaires du site (fonction validate). Si un champ n'a pas une valeur attendue, il deviendra rouge.

Pour utiliser le script, il faut :

1) rajouter en entête (<head>) de la page la ligne suivante :
   <script src="validate_forms.js" type="text/javascript"></script>

2) dans l'élément <form>, rajouter l'attribut suivant :
   onsubmit="return validate(this);"

3) dans chaque élément des formulaires, rajouter le type de données qu'on attend, au moyen de l'attribut class. Les différents types possibles sont :
   - "string"
   - "number"
   - "email"
   - "agree-required"

   Si une valeur ne peut pas être vide, alors on peut lui rajouter la classe "required"
   Exemple : <input type="text" class="string required" value="" name="Titre">

*/



// Checkboxes handling

function getElementsByClass(searchClass, tag) {
  var classElements = new Array();
  if (tag == null)
    tag = '*';
  var els = document.getElementsByTagName(tag);
  var elsLen = els.length;
  var pattern = new RegExp("(^|\\\\s)"+searchClass+"(\\\\s|$)");
  for (i = 0, j = 0; i < elsLen; i++)
  {
    if (pattern.test(els[i].className))
    {
      classElements[j] = els[i];
      j++;
    }
  }
return classElements;
}

function allUnchecked(checkBoxesList)
{
  all = true;
  for (var i=0; i<checkBoxesList.length; i++)
    if (checkBoxesList[i].checked == true)
      all = false;
  return all;
}

function checkCheckBoxes(checkBoxesList)
{
  for (var i=0; i<checkBoxesList.length; i++)
    checkBoxesList[i].checked = true;
}

function unCheckCheckBoxes(checkBoxesList)
{
  for (var i=0; i<checkBoxesList.length; i++)
    checkBoxesList[i].checked = false;
}

function checkboxInfos(field)
{
  classes = field.className.split(' ');
  var type = "";
  var group = "";
  for (var iClassCounter=0; iClassCounter<classes.length; iClassCounter++)
  {
    currentClass = classes[iClassCounter];
    // class format example : 'checkbox-parent-1'
    if (currentClass.indexOf('checkbox', 0) != -1)
    {
      infos = currentClass.split('-');
      type = infos[1];
      group = infos[2];
    }
  }
  return [type, group];
}

function clickCheckBox(field)
{
  chckInfos = checkboxInfos(field);
  checkBoxType = chckInfos[0];
  checkBoxesGroup = chckInfos[1];
  associatedCheckBoxes = [];
  if (checkBoxType == 'parent')
  {
    associatedClass = 'checkbox-child-' + checkBoxesGroup;
    associatedCheckBoxes = getElementsByClass(associatedClass, 'input');
    if (field.checked)
      checkCheckBoxes(associatedCheckBoxes);
    else
      unCheckCheckBoxes(associatedCheckBoxes);
  }
  else if (checkBoxType == 'child')
  {
    associatedClass = 'checkbox-parent-' + checkBoxesGroup;
    parentCheckBox = getElementsByClass(associatedClass, 'input');
    if (field.checked)
      checkCheckBoxes(parentCheckBox);
    else
      childsClass = 'checkbox-child-' + checkBoxesGroup;
      associatedChildsCheckBoxes = getElementsByClass(childsClass, 'input');
      if (allUnchecked(associatedChildsCheckBoxes))
        unCheckCheckBoxes(parentCheckBox);
  }
}


// Fields validatiors

function isNotEmpty(str)
{
  return ((str != '') && (str != '...'));
}

function isEmpty(str)
{
  return (!(isNotEmpty(str)));
}

function isString(str)
{
  return (typeof str == 'string' && isNaN(str) || isEmpty(str));
}

function isNumber(str)
{
  return (!isNaN(str) || isEmpty(str));
}

function isEmail(str)
{
  var pattern = /^[\w-\.\']{1,}\@([\da-zA-Z-]{1,}\.){1,}[\da-zA-Z-]{2,}$/;
  return (pattern.test(str) || isEmpty(str));
}

function validateAgree(field, lang)
{
 if (lang=="FR")      {var msg = "Il faut accepter nos termes et conditions avant de continuer !";}
 else if (lang=="NL") {var msg = "Please note that you must accept our terms of services !";}
 else                 {var msg = "Please note that you must accept our terms of services !";}

 if (!field.checked){
  alert (msg);
  return false;
 }
 return true;
}


// Form validation

function validate(objForm)
{
  var arClass, bValid;
  var objField = objForm.getElementsByTagName('*');
  var password = ""
  
  for (var iFieldCounter=0; iFieldCounter<objField.length; iFieldCounter++)
  {
    arClass = objField[iFieldCounter].className.split(' ');
    for (var iClassCounter=0; iClassCounter<arClass.length; iClassCounter++)
    {
      switch (arClass[iClassCounter])
      {
        case 'password':
           password = objField[iFieldCounter].value
           bValid = isString(objField[iFieldCounter].value.replace(/^\s*|\s*$/g, ''));
           break;
        case 'password-confirm':
           bValid = (password == objField[iFieldCounter].value)
           break;
        case 'agree-required':
           bValid = validateAgree(objField[iFieldCounter], 'FR');
           break;
        case 'required':
           bValid = isNotEmpty(objField[iFieldCounter].value.replace(/^\s*|\s*$/g, ''));
           break;
        case 'string':
           bValid = isString(objField[iFieldCounter].value.replace(/^\s*|\s*$/g, ''));
           break;
        case 'number' :
           bValid = isNumber(objField[iFieldCounter].value);
           break;
        case 'email' :
           bValid = isEmail(objField[iFieldCounter].value);
           break;
        default:
           bValid = true;
      }

      if (bValid == false)
      {
        // TESTS
        // alert(objField[iFieldCounter].className);
        // alert('Mauvaise valeur de ' + objField[iFieldCounter].name);
        // objField[iFieldCounter].select();

        objField[iFieldCounter].focus();
        objField[iFieldCounter].style.background='Red';
        window.scrollBy(0,-150);

        // Avoid Plone re-submit warning
        submittingFields = getElementsByClass('submitting');
        for (var i=0; i<submittingFields.length; i++)
          removeClassName(submittingFields[i], 'submitting');

        return false;
      }
      else
        objField[iFieldCounter].style.background='';
    }
  }
 return true;
}
