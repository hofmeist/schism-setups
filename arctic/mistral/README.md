# Running the Arctic Setup on mistral:

a) check project number and email address in the header of the runscripts:
  run_icehotstart.sh
  run_hotstart.sh
  merge_outut.sh
  merge_hotstart.sh

b) start simulation with the python script start_simulation.py from the setup directory (not in "mistral" directory)

  python mistral/start_icesimulation.py [id_of_simulation] [first yyyy-mm] [last yyyy-mm]

  e.g. python mistral/start_icesimulation.py 012 2012-01 2013-12

c) you will find the output files under /work/[project]/$USER/arctic/arctic[id_of_simulation]


